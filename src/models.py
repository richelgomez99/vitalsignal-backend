"""Pydantic models for VitalSignal API"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class RiskLevel(str, Enum):
    """Risk level classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ActionType(str, Enum):
    """Recommended action types"""
    IMMEDIATE_ALERT = "immediate_alert"
    EMAIL_NOTIFICATION = "email_notification"
    LOG_ONLY = "log_only"
    IGNORE = "ignore"


class DiseaseSeverity(str, Enum):
    """Disease outbreak severity"""
    PANDEMIC = "pandemic"
    EPIDEMIC = "epidemic"
    OUTBREAK = "outbreak"
    CLUSTER = "cluster"
    SPORADIC = "sporadic"


# User Models
class HealthCondition(BaseModel):
    """User health condition"""
    name: str
    icd10_code: Optional[str] = None
    severity: str = "moderate"  # mild, moderate, severe
    diagnosed_date: Optional[datetime] = None


class Medication(BaseModel):
    """User medication"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None


class FamilyMember(BaseModel):
    """Family member location"""
    name: str
    relationship: str
    location: str  # City, Country
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TravelPlan(BaseModel):
    """User travel plan"""
    destination: str
    departure_date: datetime
    return_date: datetime
    purpose: Optional[str] = None


class UserPreferences(BaseModel):
    """User notification preferences"""
    risk_tolerance: str = "moderate"  # low, moderate, high
    notification_threshold: RiskLevel = RiskLevel.MEDIUM
    preferred_language: str = "en"
    wants_images: bool = True
    wants_translations: bool = False


class UserProfile(BaseModel):
    """Complete user profile"""
    user_id: str
    email: EmailStr
    name: str
    age: int
    location: str  # City, Country
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Health information
    health_conditions: List[HealthCondition] = []
    medications: List[Medication] = []
    allergies: List[str] = []
    
    # Context
    family_members: List[FamilyMember] = []
    travel_plans: List[TravelPlan] = []
    
    # Preferences
    preferences: UserPreferences = UserPreferences()
    
    # Learning data
    learned_weights: Dict[str, float] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    """Model for creating a new user"""
    email: EmailStr
    name: str
    age: int
    location: str
    health_conditions: List[HealthCondition] = []
    family_members: List[FamilyMember] = []
    preferences: Optional[UserPreferences] = None


# Alert Models
class HealthAlert(BaseModel):
    """Health alert from external sources"""
    alert_id: str
    title: str
    description: str
    disease: str
    location: str  # City, Country or Region
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    severity: DiseaseSeverity
    affected_population: Optional[int] = None
    mortality_rate: Optional[float] = None
    
    source: str  # e.g., "WHO", "CDC", "ProMED"
    source_url: Optional[str] = None
    
    # Medical codes (enriched by PhenoML)
    icd10_codes: List[str] = []
    snomed_codes: List[str] = []
    fhir_data: Optional[Dict[str, Any]] = None
    
    published_at: datetime
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class AlertEnrichmentRequest(BaseModel):
    """Request to enrich alert with medical codes"""
    alert: HealthAlert
    user_profile: Optional[UserProfile] = None


# Risk Assessment Models
class RiskFactors(BaseModel):
    """Individual risk factor scores"""
    base_severity: float = Field(..., ge=0, le=1, description="Alert base severity (0-1)")
    health_vulnerability: float = Field(..., ge=0, le=1, description="User health conditions impact")
    geographic_proximity: float = Field(..., ge=0, le=1, description="Distance to outbreak")
    family_exposure: float = Field(..., ge=0, le=1, description="Family members in affected area")
    travel_risk: float = Field(..., ge=0, le=1, description="Upcoming travel to affected area")
    learned_preference: float = Field(..., ge=0, le=1, description="User's historical preferences")


class RiskScore(BaseModel):
    """Calculated risk score for a user-alert pair"""
    user_id: str
    alert_id: str
    
    # Overall score
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=1, description="Combined risk score (0-1)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in assessment")
    
    # Breakdown
    risk_factors: RiskFactors
    
    # Reasoning
    reasoning: List[str] = Field(
        ..., 
        description="Human-readable explanation of risk factors"
    )
    
    # Recommended actions
    recommended_actions: List[ActionType]
    needs_translation: bool = False
    needs_image: bool = False
    priority: int = Field(..., ge=1, le=10, description="Notification priority (1=highest)")
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizationRequest(BaseModel):
    """Request to calculate personalized risk"""
    user_id: str
    alert: HealthAlert


class PersonalizationResponse(BaseModel):
    """Response with personalized risk assessment"""
    user: UserProfile
    alert: HealthAlert
    risk_score: RiskScore
    
    # Generated content (if applicable)
    translated_content: Optional[Dict[str, str]] = None
    generated_image_url: Optional[str] = None
    
    # Metadata
    processing_time_ms: float
    external_apis_called: List[str]


# Feedback Models
class FeedbackType(str, Enum):
    """User feedback types"""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    TOO_SENSITIVE = "too_sensitive"
    NOT_SENSITIVE_ENOUGH = "not_sensitive_enough"
    FALSE_POSITIVE = "false_positive"


class FeedbackEvent(BaseModel):
    """User feedback on a risk assessment"""
    feedback_id: str = Field(default_factory=lambda: f"fb_{datetime.utcnow().timestamp()}")
    user_id: str
    alert_id: str
    
    feedback_type: FeedbackType
    user_comment: Optional[str] = None
    
    # Original assessment for learning
    original_risk_score: float
    original_risk_level: RiskLevel
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackRequest(BaseModel):
    """Request to submit feedback"""
    user_id: str
    alert_id: str
    feedback_type: FeedbackType
    comment: Optional[str] = None


# Health Check Models
class HealthStatus(BaseModel):
    """Service health status"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "0.1.0"
    database_connected: bool = False
    external_services: Dict[str, bool] = {}


class MetricsResponse(BaseModel):
    """Decision metrics"""
    total_assessments: int
    assessments_by_risk_level: Dict[RiskLevel, int]
    average_processing_time_ms: float
    external_api_calls: Dict[str, int]
    feedback_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
