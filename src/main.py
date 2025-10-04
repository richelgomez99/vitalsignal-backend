"""
VitalSignal Personal Health Guardian API

Main FastAPI application providing intelligent, personalized health risk assessment.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from typing import List, Optional
import time
from datetime import datetime

from pydantic import BaseModel
from src.models import (
    UserProfile, UserCreate, HealthAlert, PersonalizationRequest,
    PersonalizationResponse, RiskScore, FeedbackRequest, FeedbackEvent,
    HealthStatus, MetricsResponse
)
from src.risk_calculator import risk_calculator
from src.utils.clickhouse_client import db_client
from src.config import settings
from src.services.structify_service import structify_service
from src.services.phenoml_service import phenoml_service
from src.services.deepl_service import deepl_service
from src.services.freepik_service import freepik_service
from src.services.sendgrid_service import sendgrid_service


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

# Mount static files for serving Freepik generated images
app.mount("/static", StaticFiles(directory="static"), name="static")


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
    
    # Smart ID mapping - handle common variations from AI agents
    user_id_map = {
        # Exact IDs
        "demo_maria": "demo_maria",
        "demo_john": "demo_john",
        "demo_sarah": "demo_sarah",
        "demo_kwame": "demo_kwame",
        "demo_aisha": "demo_aisha",
        # Common AI variations
        "maria": "demo_maria",
        "maria_silva": "demo_maria",
        "maria_silva_id": "demo_maria",
        "john": "demo_john",
        "john_smith": "demo_john",
        "john_smith_id": "demo_john",
        "sarah": "demo_sarah",
        "sarah_chen": "demo_sarah",
        "kwame": "demo_kwame",
        "kwame_osei": "demo_kwame",
        "aisha": "demo_aisha",
        "aisha_hassan": "demo_aisha",
    }
    
    # Map the user_id to canonical ID
    canonical_id = user_id_map.get(request.user_id.lower(), request.user_id)
    
    # Get user profile
    user = db_client.get_user(canonical_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {request.user_id} not found. Available users: demo_maria, demo_john"
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


class MedicalEnrichmentRequest(BaseModel):
    """Request to enrich disease with medical codes"""
    disease_name: str
    description: Optional[str] = ""


class TranslationRequest(BaseModel):
    """Request to translate text"""
    text: str
    target_language: str
    source_language: Optional[str] = None


class ImageGenerationRequest(BaseModel):
    """Request to generate alert image"""
    disease_name: str
    severity: str
    location: str


class EmailNotificationRequest(BaseModel):
    """Request to send email notification"""
    to_email: str
    user_name: str
    disease_name: str
    location: str
    risk_level: str
    risk_score: float
    reasoning: list
    image_url: Optional[str] = None
    family_report: Optional[str] = None


@app.get("/api/v1/explain-disease", tags=["Medical"])
async def explain_disease_for_patient(disease_name: str, icd10_code: str = "", snomed_code: str = ""):
    """
    Explain disease in patient-friendly language using PhenoML
    
    Converts medical codes and jargon into plain language that patients can understand.
    Includes symptoms, transmission, prevention, and care recommendations.
    
    Args:
        disease_name: Name of the disease
        icd10_code: ICD-10 medical code (optional)
        snomed_code: SNOMED medical code (optional)
        
    Returns:
        Plain language explanation with actionable information
    """
    try:
        explanation = await phenoml_service.explain_medical_codes(
            disease_name, icd10_code, snomed_code
        )
        return explanation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease explanation failed: {str(e)}"
        )


@app.post("/api/v1/enrich-medical", tags=["Medical"])
async def enrich_with_medical_codes(request: MedicalEnrichmentRequest):
    """
    Enrich disease with FHIR/SNOMED/ICD-10 medical codes using PhenoML
    
    Args:
        request: Disease name and optional description
        
    Returns:
        Medical codes and FHIR data
        
    ## For Demo:
    - Shows medical intelligence
    - Standardized medical coding
    - FHIR interoperability
    
    ## Example:
    ```json
    {
      "disease_name": "dengue",
      "description": "fever and rash"
    }
    ```
    """
    try:
        enriched_data = await phenoml_service.enrich_disease(
            request.disease_name, 
            request.description
        )
        return enriched_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Medical enrichment failed: {str(e)}"
        )


class FamilyReportRequest(BaseModel):
    """Request to generate family-shareable report"""
    user_name: str
    disease_name: str
    location: str
    risk_level: str
    risk_score: float
    reasoning: list
    target_language: str  # Language code (ES, FR, PT, etc.)


@app.post("/api/v1/translate", tags=["Translation"])
async def translate_text(request: TranslationRequest):
    """
    Translate health alert text using DeepL
    
    Args:
        request: Text and target language
        
    Returns:
        Translated text and language metadata
    """
    try:
        result = await deepl_service.translate_text(
            request.text,
            request.target_language,
            request.source_language
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@app.post("/api/v1/generate-family-report", tags=["Translation"])
async def generate_family_report(request: FamilyReportRequest):
    """
    Generate a comprehensive, translated family health guide using PhenoML + DeepL
    
    Creates an actionable report with medical information, symptoms to watch for,
    and prevention steps - translated for family members.
    
    Args:
        request: User info, risk assessment, and target language
        
    Returns:
        Translated family health guide
    """
    try:
        # Get medical information from PhenoML
        medical_info = await phenoml_service.explain_medical_codes(
            request.disease_name, "", ""
        )
        
        priority_text = {
            "CRITICAL": "🚨 URGENT - CRITICAL PRIORITY",
            "HIGH": "⚠️ IMPORTANT - HIGH PRIORITY",
            "MEDIUM": "⚡ MODERATE CONCERN",
            "LOW": "ℹ️ INFORMATIONAL"
        }.get(request.risk_level, "HEALTH INFORMATION")
        
        # Build comprehensive family guide
        english_report = f"""
🏥 FAMILY HEALTH GUIDE: {request.disease_name.upper()}

Dear Family of {request.user_name},

{request.user_name} has been identified as having {request.risk_level} risk for {request.disease_name} in {request.location}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RISK ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priority Level: {priority_text}
Risk Score: {request.risk_score:.2f} out of 1.00

Why This Matters:
{chr(10).join(f'• {reason}' for reason in request.reasoning)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🩺 WHAT IS {request.disease_name.upper()}?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{medical_info.get('what_it_is', 'A health condition requiring attention.')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👀 SYMPTOMS TO WATCH FOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Monitor {request.user_name} for these symptoms:
{chr(10).join(f'• {symptom}' for symptom in medical_info.get('common_symptoms', ['Consult healthcare provider']))}

If you notice any of these symptoms, take them seriously and seek medical attention.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🦠 HOW IT SPREADS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{medical_info.get('how_it_spreads', 'Contact health authorities for information.')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ PREVENTION & PROTECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What the family should do:
{chr(10).join(f'• {tip}' for tip in medical_info.get('prevention_tips', ['Follow health authority guidelines']))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚑 WHEN TO SEEK IMMEDIATE CARE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{medical_info.get('when_to_seek_care', 'Seek medical attention if symptoms worsen or if you have concerns.')}

If {request.user_name} shows severe symptoms or the condition worsens rapidly, do not wait - get medical help immediately.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍👩‍👧‍👦 FAMILY ACTION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Stay in regular contact with {request.user_name}
2. Help them follow prevention measures
3. Watch for warning symptoms
4. Keep emergency contact numbers handy
5. Share this guide with other family members
6. Follow local health authority updates for {request.location}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This family health guide is powered by VitalSignal AI and PhenoML medical intelligence.
Generated for the family of {request.user_name} to provide clear, actionable health information.

Stay vigilant, stay informed, and support each other.

🏥 VitalSignal Health Guardian
"""
        
        # Skip translation if English requested
        if request.target_language.upper() == "EN":
            return {
                "original_report": english_report,
                "translated_report": english_report,
                "target_language": "EN",
                "user_name": request.user_name,
                "disease": request.disease_name,
                "risk_level": request.risk_level,
                "shareable": True,
                "note": "Report in English (no translation needed)"
            }
        
        # Translate to family's language using DeepL
        translation_result = await deepl_service.translate_text(
            english_report,
            request.target_language
        )
        
        return {
            "original_report": english_report,
            "translated_report": translation_result["translated_text"],
            "target_language": request.target_language,
            "detected_source": translation_result.get("detected_source_language", "EN"),
            "user_name": request.user_name,
            "disease": request.disease_name,
            "risk_level": request.risk_level,
            "shareable": True,
            "note": f"Report translated to {request.target_language} for family sharing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Family report generation failed: {str(e)}"
        )


@app.get("/api/v1/generate-symptom-visual", tags=["Images"])
async def generate_symptom_visual(disease_name: str):
    """
    Generate visual guide showing what disease symptoms look like
    
    Creates an educational visual showing common symptoms for the disease.
    Useful for patients to recognize symptoms early.
    
    Args:
        disease_name: Name of the disease
        
    Returns:
        Image URL for symptom visualization
    """
    try:
        result = await freepik_service.generate_symptom_visual(disease_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom visual generation failed: {str(e)}"
        )


@app.get("/api/v1/generate-prevention-poster", tags=["Images"])
async def generate_prevention_poster(disease_name: str, language: str = "EN"):
    """
    Generate multilingual prevention infographic using Freepik
    
    Creates a shareable, printable prevention poster in the specified language.
    Perfect for families to print and share in their community.
    
    Args:
        disease_name: Name of the disease
        language: Language code (EN, ES, PT-BR, FR, AR, ZH, etc.)
        
    Returns:
        Image URL for prevention infographic
    """
    try:
        result = await freepik_service.generate_prevention_infographic(disease_name, language)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prevention poster generation failed: {str(e)}"
        )


@app.post("/api/v1/generate-image", tags=["Images"])
async def generate_alert_image(request: ImageGenerationRequest):
    """
    Generate visual alert image using Freepik AI
    
    Args:
        request: Disease info for image generation
        
    Returns:
        Image URL and metadata
    """
    try:
        result = await freepik_service.generate_alert_image(
            request.disease_name,
            request.severity,
            request.location
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )


@app.post("/api/v1/send-notification", tags=["Notifications"])
async def send_email_notification(request: EmailNotificationRequest):
    """
    Send personalized email notification using SendGrid
    
    Automatically enriches with PhenoML medical information for patient education.
    
    Args:
        request: Email content and recipient info
        
    Returns:
        Delivery status
    """
    try:
        # Get patient-friendly medical explanation from PhenoML
        medical_codes = await phenoml_service.explain_medical_codes(
            request.disease_name,
            "",  # ICD-10 code (optional)
            ""   # SNOMED code (optional)
        )
        
        result = await sendgrid_service.send_email(
            request.to_email,
            request.user_name,
            request.disease_name,
            request.location,
            request.risk_level,
            request.risk_score,
            request.reasoning,
            request.image_url,
            request.family_report,
            medical_codes
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email notification failed: {str(e)}"
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


@app.get("/api/v1/images/{image_id}", tags=["Images"])
async def get_image(image_id: str):
    """
    Retrieve generated image from ClickHouse
    
    Images are stored in ClickHouse database after being generated by Freepik AI.
    This endpoint serves them with proper JPEG content type.
    
    Args:
        image_id: Unique image identifier
        
    Returns:
        Image as JPEG bytes
    """
    try:
        image_data = db_client.get_image(image_id)
        if image_data:
            return Response(content=image_data, media_type="image/jpeg")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image not found: {image_id}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving image: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
