"""ClickHouse database client"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import clickhouse_connect

from src.config import settings
from src.models import UserProfile, HealthAlert, RiskScore, FeedbackEvent


class ClickHouseClient:
    """ClickHouse database client for VitalSignal"""
    
    def __init__(self):
        """Initialize ClickHouse connection"""
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish connection to ClickHouse"""
        try:
            self.client = clickhouse_connect.get_client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                username=settings.clickhouse_user,
                password=settings.clickhouse_password,
                database=settings.clickhouse_database,
                secure=settings.clickhouse_secure
            )
            print(f"✅ Connected to ClickHouse: {settings.clickhouse_host}")
        except Exception as e:
            print(f"❌ ClickHouse connection failed: {e}")
            self.client = None
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        if not self.client:
            return False
        try:
            result = self.client.command("SELECT 1")
            return result == 1
        except:
            return False
    
    # User operations
    def create_user(self, user: UserProfile) -> bool:
        """Create a new user"""
        try:
            self.client.insert('users', [[
                user.user_id,
                user.email,
                user.name,
                user.age,
                user.location,
                user.latitude,
                user.longitude,
                json.dumps([c.dict() for c in user.health_conditions]),
                json.dumps([m.dict() for m in user.medications]),
                json.dumps(user.allergies),
                json.dumps([f.dict() for f in user.family_members]),
                json.dumps([t.dict() for t in user.travel_plans]),
                json.dumps(user.preferences.dict()),
                json.dumps(user.learned_weights),
                user.created_at,
                user.updated_at
            ]])
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID"""
        try:
            result = self.client.query(
                "SELECT * FROM users WHERE user_id = {user_id:String}",
                parameters={"user_id": user_id}
            )
            
            if not result.result_rows:
                return None
            
            row = result.result_rows[0]
            return self._row_to_user(row)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[UserProfile]:
        """Get all users"""
        try:
            result = self.client.query("SELECT * FROM users ORDER BY created_at DESC")
            return [self._row_to_user(row) for row in result.result_rows]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def _row_to_user(self, row) -> UserProfile:
        """Convert database row to UserProfile"""
        from src.models import HealthCondition, Medication, FamilyMember, TravelPlan, UserPreferences
        
        return UserProfile(
            user_id=row[0],
            email=row[1],
            name=row[2],
            age=row[3],
            location=row[4],
            latitude=row[5],
            longitude=row[6],
            health_conditions=[HealthCondition(**c) for c in json.loads(row[7])],
            medications=[Medication(**m) for m in json.loads(row[8])],
            allergies=json.loads(row[9]),
            family_members=[FamilyMember(**f) for f in json.loads(row[10])],
            travel_plans=[TravelPlan(**t) for t in json.loads(row[11])],
            preferences=UserPreferences(**json.loads(row[12])),
            learned_weights=json.loads(row[13]),
            created_at=row[14],
            updated_at=row[15]
        )
    
    # Alert operations
    def save_alert(self, alert: HealthAlert) -> bool:
        """Save a health alert"""
        try:
            self.client.insert('health_alerts', [[
                alert.alert_id,
                alert.title,
                alert.description,
                alert.disease,
                alert.location,
                alert.latitude,
                alert.longitude,
                alert.severity.value,
                alert.affected_population,
                alert.mortality_rate,
                alert.source,
                alert.source_url,
                json.dumps(alert.icd10_codes),
                json.dumps(alert.snomed_codes),
                json.dumps(alert.fhir_data) if alert.fhir_data else "{}",
                alert.published_at,
                alert.scraped_at
            ]])
            return True
        except Exception as e:
            print(f"Error saving alert: {e}")
            return False
    
    # Risk assessment operations
    def save_risk_assessment(self, risk_score: RiskScore, processing_time_ms: float, apis_called: List[str]) -> bool:
        """Save a risk assessment"""
        try:
            assessment_id = f"assess_{datetime.utcnow().timestamp()}"
            
            self.client.insert('risk_assessments', [[
                assessment_id,
                risk_score.user_id,
                risk_score.alert_id,
                risk_score.risk_level.value,
                risk_score.risk_score,
                risk_score.confidence,
                risk_score.risk_factors.base_severity,
                risk_score.risk_factors.health_vulnerability,
                risk_score.risk_factors.geographic_proximity,
                risk_score.risk_factors.family_exposure,
                risk_score.risk_factors.travel_risk,
                risk_score.risk_factors.learned_preference,
                json.dumps([a.value for a in risk_score.recommended_actions]),
                risk_score.needs_translation,
                risk_score.needs_image,
                risk_score.priority,
                json.dumps(risk_score.reasoning),
                processing_time_ms,
                json.dumps(apis_called),
                risk_score.calculated_at
            ]])
            return True
        except Exception as e:
            print(f"Error saving risk assessment: {e}")
            return False
    
    # Feedback operations
    def save_feedback(self, feedback: FeedbackEvent) -> bool:
        """Save user feedback"""
        try:
            self.client.insert('feedback_events', [[
                feedback.feedback_id,
                feedback.user_id,
                feedback.alert_id,
                feedback.feedback_type.value,
                feedback.user_comment,
                feedback.original_risk_score,
                feedback.original_risk_level.value,
                feedback.created_at
            ]])
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    # Metrics operations
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            # Total assessments
            total = self.client.query("SELECT count() FROM risk_assessments").result_rows[0][0]
            
            # By risk level
            by_level = self.client.query("""
                SELECT risk_level, count() 
                FROM risk_assessments 
                GROUP BY risk_level
            """).result_rows
            
            # Average processing time
            avg_time = self.client.query("""
                SELECT avg(processing_time_ms) 
                FROM risk_assessments
            """).result_rows[0][0]
            
            # API calls
            api_calls = self.client.query("""
                SELECT service_name, count() 
                FROM api_call_logs 
                GROUP BY service_name
            """).result_rows if self.client.query("EXISTS TABLE api_call_logs").result_rows[0][0] else []
            
            # Feedback count
            feedback = self.client.query("SELECT count() FROM feedback_events").result_rows[0][0]
            
            return {
                "total_assessments": total,
                "assessments_by_risk_level": {level: count for level, count in by_level},
                "average_processing_time_ms": avg_time or 0,
                "external_api_calls": {service: count for service, count in api_calls},
                "feedback_count": feedback
            }
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return {
                "total_assessments": 0,
                "assessments_by_risk_level": {},
                "average_processing_time_ms": 0,
                "external_api_calls": {},
                "feedback_count": 0
            }
    
    def log_api_call(self, service: str, endpoint: str, method: str, 
                     status: int, response_time: float, success: bool, 
                     error: Optional[str] = None):
        """Log external API call"""
        try:
            call_id = f"call_{datetime.utcnow().timestamp()}"
            self.client.insert('api_call_logs', [[
                call_id,
                service,
                endpoint,
                method,
                status,
                response_time,
                success,
                error,
                None,
                None,
                datetime.utcnow()
            ]])
        except Exception as e:
            print(f"Error logging API call: {e}")


# Global instance
db_client = ClickHouseClient()
