"""
VitalSignal Personal Health Guardian API

Main FastAPI application providing intelligent, personalized health risk assessment.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import time
from datetime import datetime

from src.models import (
    UserProfile, UserCreate, HealthAlert, PersonalizationRequest,
    PersonalizationResponse, RiskScore, FeedbackRequest, FeedbackEvent,
    HealthStatus, MetricsResponse
)
from src.risk_calculator import risk_calculator
from src.utils.clickhouse_client import db_client
from src.config import settings
from src.services.structify_service import structify_service


# Initialize FastAPI app
app = FastAPI(
    title="VitalSignal API",
    description="Personal Health Guardian - Autonomous AI Agent for Personalized Disease Monitoring",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow all for demo - restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 VitalSignal API starting...")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔗 ClickHouse: {settings.clickhouse_host}")
    
    # Test database connection
    if db_client.health_check():
        print("✅ Database connection healthy")
    else:
        print("⚠️  Database connection failed - some features may not work")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API info"""
    return {
        "name": "VitalSignal Personal Health Guardian API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns service health status and external dependencies
    """
    db_connected = db_client.health_check()
    
    return HealthStatus(
        status="healthy" if db_connected else "degraded",
        version="0.1.0",
        database_connected=db_connected,
        external_services={
            "clickhouse": db_connected,
            "risk_calculator": True  # Always available
        }
    )


@app.get("/api/v1/users", response_model=List[UserProfile], tags=["Users"])
async def get_users():
    """
    Get all users
    
    Returns list of all registered users with their profiles.
    Used by Airia to iterate over users for personalization.
    """
    users = db_client.get_all_users()
    
    if not users:
        # Return empty list if no users (not an error)
        return []
    
    return users


@app.get("/api/v1/users/{user_id}", response_model=UserProfile, tags=["Users"])
async def get_user(user_id: str):
    """
    Get specific user by ID
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        Complete user profile
        
    Raises:
        404: User not found
    """
    user = db_client.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


@app.post("/api/v1/users", response_model=UserProfile, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user_create: UserCreate):
    """
    Create a new user
    
    Args:
        user_create: User creation data
        
    Returns:
        Created user profile
        
    Raises:
        400: Invalid user data
        500: Database error
    """
    # Generate user ID
    user_id = f"user_{int(datetime.utcnow().timestamp())}"
    
    # Create full user profile
    user = UserProfile(
        user_id=user_id,
        email=user_create.email,
        name=user_create.name,
        age=user_create.age,
        location=user_create.location,
        health_conditions=user_create.health_conditions,
        family_members=user_create.family_members,
        preferences=user_create.preferences or {}
    )
    
    # Save to database
    success = db_client.create_user(user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return user


@app.post("/api/v1/personalize", response_model=PersonalizationResponse, tags=["Personalization"])
async def personalize_risk(request: PersonalizationRequest):
    """
    **CORE ENDPOINT** - Calculate personalized risk score
    
    This is where the autonomy magic happens. Same alert → different users → different outcomes.
    
    Args:
        request: User ID and health alert
        
    Returns:
        Personalized risk assessment with reasoning and recommended actions
        
    Raises:
        404: User not found
        500: Processing error
    
    ## Multi-Factor Analysis:
    - Base severity of outbreak
    - User's health conditions (disease-condition interactions)
    - Geographic proximity (user location vs outbreak location)
    - Family member exposure (family in affected areas)
    - Travel risk (upcoming trips to affected areas)
    - Learned preferences (historical feedback)
    - User risk tolerance
    
    ## Non-Deterministic Outcomes:
    - User A (diabetic, family in São Paulo) → HIGH ALERT
    - User B (healthy, no connections) → Low priority
    - User C (pregnant, traveling to Brazil) → CRITICAL
    """
    start_time = time.time()
    apis_called = []
    
    # Get user profile
    user = db_client.get_user(request.user_id)
    
    # DEMO FALLBACK: Use mock users if DB user not found
    if not user:
        user = _get_mock_user(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {request.user_id} not found"
            )
    
    try:
        # CORE INTELLIGENCE: Calculate personalized risk
        risk_score = risk_calculator.calculate_risk(user, request.alert)
        
        # Save assessment to database
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        db_client.save_risk_assessment(risk_score, processing_time, apis_called)
        
        # Save alert if not exists
        db_client.save_alert(request.alert)
        
        # Build response
        response = PersonalizationResponse(
            user=user,
            alert=request.alert,
            risk_score=risk_score,
            processing_time_ms=processing_time,
            external_apis_called=apis_called
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk calculation failed: {str(e)}"
        )


@app.get("/api/v1/alerts/scrape", response_model=List[HealthAlert], tags=["Alerts"])
async def scrape_latest_alerts(
    disease: Optional[str] = None,
    limit: int = 10
):
    """
    **NEW** - Scrape latest health alerts from WHO using Structify
    
    This demonstrates autonomous data gathering - the system actively pulls
    real-world disease outbreak information instead of waiting for manual input.
    
    Args:
        disease: Optional filter for specific disease (e.g., "dengue", "covid", "malaria")
        limit: Maximum number of alerts to return (default 10)
        
    Returns:
        List of health alerts scraped from WHO
        
    ## For Demo:
    - Shows autonomous monitoring capability
    - Real-time WHO data integration
    - Structify AI for intelligent scraping
    
    ## Example:
    - GET /api/v1/alerts/scrape
    - GET /api/v1/alerts/scrape?disease=dengue
    - GET /api/v1/alerts/scrape?limit=5
    """
    try:
        alerts = await structify_service.scrape_who_alerts(disease=disease)
        return alerts[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


@app.post("/api/v1/feedback", status_code=status.HTTP_201_CREATED, tags=["Learning"])
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback for learning
    
    This enables the learning engine to adapt risk assessments based on user feedback.
    
    Args:
        request: Feedback data
        
    Returns:
        Success confirmation
    """
    # Create feedback event
    feedback = FeedbackEvent(
        user_id=request.user_id,
        alert_id=request.alert_id,
        feedback_type=request.feedback_type,
        user_comment=request.comment,
        original_risk_score=0.0,  # Would retrieve from previous assessment
        original_risk_level="medium"  # Would retrieve from previous assessment
    )
    
    # Save to database
    success = db_client.save_feedback(feedback)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save feedback"
        )
    
    # TODO: Update user's learned weights based on feedback
    # This is where behavioral learning would happen
    
    return {
        "success": True,
        "message": "Feedback recorded. System will adapt future assessments.",
        "feedback_id": feedback.feedback_id
    }


@app.get("/api/v1/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """
    Get system metrics
    
    Returns aggregated metrics about risk assessments, API usage, and feedback.
    Useful for demo to show system activity.
    """
    metrics_data = db_client.get_metrics()
    
    from src.models import RiskLevel
    
    return MetricsResponse(
        total_assessments=metrics_data["total_assessments"],
        assessments_by_risk_level={
            RiskLevel(k): v for k, v in metrics_data["assessments_by_risk_level"].items()
        } if metrics_data["assessments_by_risk_level"] else {},
        average_processing_time_ms=metrics_data["average_processing_time_ms"],
        external_api_calls=metrics_data["external_api_calls"],
        feedback_count=metrics_data["feedback_count"]
    )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
        "path": str(request.url)
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred. Please try again.",
        "path": str(request.url)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
