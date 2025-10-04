"""
Risk Calculator - Core Autonomy Logic

This module implements the intelligent, non-deterministic decision-making that
demonstrates true autonomy. Same alert → different users → different outcomes.
"""

from typing import List, Tuple, Dict
from datetime import datetime, timedelta
import math

from src.models import (
    UserProfile, HealthAlert, RiskScore, RiskFactors, RiskLevel, 
    ActionType, DiseaseSeverity, HealthCondition, FamilyMember, TravelPlan
)


class RiskCalculator:
    """
    Calculates personalized risk scores based on multiple factors.
    
    This is where the magic happens - multi-factor reasoning that produces
    non-deterministic, user-specific outcomes.
    """
    
    # Disease severity weights
    SEVERITY_WEIGHTS = {
        DiseaseSeverity.PANDEMIC: 1.0,
        DiseaseSeverity.EPIDEMIC: 0.8,
        DiseaseSeverity.OUTBREAK: 0.6,
        DiseaseSeverity.CLUSTER: 0.4,
        DiseaseSeverity.SPORADIC: 0.2,
    }
    
    # Risk tolerance multipliers
    RISK_TOLERANCE_MULTIPLIERS = {
        "low": 1.5,      # More sensitive to risks
        "moderate": 1.0,  # Balanced
        "high": 0.7,      # Less sensitive to risks
    }
    
    def __init__(self, medical_knowledge: Dict = None):
        """
        Initialize risk calculator with medical knowledge base
        
        Args:
            medical_knowledge: Disease-condition interaction matrix
        """
        self.medical_knowledge = medical_knowledge or self._default_medical_knowledge()
    
    def calculate_risk(
        self, 
        user: UserProfile, 
        alert: HealthAlert
    ) -> RiskScore:
        """
        Calculate personalized risk score for a user-alert pair
        
        This is the core autonomy demonstration:
        - Multi-factor analysis (8+ variables)
        - Medical knowledge integration
        - Geographic calculations
        - Temporal reasoning (travel plans)
        - User preference learning
        
        Args:
            user: User profile with health and context
            alert: Health alert to assess
            
        Returns:
            Complete risk score with reasoning
        """
        # Calculate individual risk factors
        base_severity = self._calculate_base_severity(alert)
        health_vulnerability = self._calculate_health_vulnerability(user, alert)
        geographic_proximity = self._calculate_geographic_proximity(user, alert)
        family_exposure = self._calculate_family_exposure(user, alert)
        travel_risk = self._calculate_travel_risk(user, alert)
        learned_preference = self._get_learned_preference(user, alert)
        
        # Create risk factors breakdown
        risk_factors = RiskFactors(
            base_severity=base_severity,
            health_vulnerability=health_vulnerability,
            geographic_proximity=geographic_proximity,
            family_exposure=family_exposure,
            travel_risk=travel_risk,
            learned_preference=learned_preference
        )
        
        # Calculate weighted composite score
        composite_score = self._calculate_composite_score(risk_factors, user)
        
        # Apply user risk tolerance
        tolerance_multiplier = self.RISK_TOLERANCE_MULTIPLIERS.get(
            user.preferences.risk_tolerance, 1.0
        )
        final_score = min(composite_score * tolerance_multiplier, 1.0)
        
        # Classify risk level
        risk_level = self._classify_risk_level(final_score)
        
        # Generate human-readable reasoning
        reasoning = self._generate_reasoning(user, alert, risk_factors)
        
        # Determine recommended actions
        recommended_actions = self._determine_actions(risk_level, final_score)
        
        # Check if translation/image needed
        needs_translation = (
            user.preferences.wants_translations and 
            user.preferences.preferred_language != "en" and
            risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        needs_image = (
            user.preferences.wants_images and
            risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        # Calculate priority (1-10, lower = higher priority)
        priority = self._calculate_priority(final_score)
        
        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(user, alert)
        
        return RiskScore(
            user_id=user.user_id,
            alert_id=alert.alert_id,
            risk_level=risk_level,
            risk_score=final_score,
            confidence=confidence,
            risk_factors=risk_factors,
            reasoning=reasoning,
            recommended_actions=recommended_actions,
            needs_translation=needs_translation,
            needs_image=needs_image,
            priority=priority
        )
    
    def _calculate_base_severity(self, alert: HealthAlert) -> float:
        """Calculate base severity from alert"""
        base = self.SEVERITY_WEIGHTS.get(alert.severity, 0.5)
        
        # Adjust for mortality rate if available
        if alert.mortality_rate:
            mortality_factor = min(alert.mortality_rate / 10.0, 1.0)  # Normalize to 0-1
            base = (base + mortality_factor) / 2
        
        return min(base, 1.0)
    
    def _calculate_health_vulnerability(self, user: UserProfile, alert: HealthAlert) -> float:
        """
        Calculate user's health vulnerability to this specific disease
        
        Uses medical knowledge base to find disease-condition interactions
        """
        if not user.health_conditions:
            return 0.0
        
        vulnerability_scores = []
        
        for condition in user.health_conditions:
            # Get interaction multiplier from medical knowledge
            multiplier = self.medical_knowledge.get(alert.disease, {}).get(
                condition.name.lower(), 1.0
            )
            
            # Weight by condition severity
            severity_weight = {"mild": 0.3, "moderate": 0.6, "severe": 1.0}.get(
                condition.severity, 0.6
            )
            
            vulnerability_scores.append(multiplier * severity_weight)
        
        # Return maximum vulnerability (most concerning condition)
        return min(max(vulnerability_scores), 1.0) if vulnerability_scores else 0.0
    
    def _calculate_geographic_proximity(self, user: UserProfile, alert: HealthAlert) -> float:
        """
        Calculate geographic proximity using simplified distance
        
        In production: use Haversine formula with real coordinates
        For MVP: string matching on location
        """
        if not alert.location:
            return 0.3  # Unknown location = moderate proximity
        
        user_location_lower = user.location.lower()
        alert_location_lower = alert.location.lower()
        
        # Extract city/country
        user_parts = user_location_lower.split(",")
        alert_parts = alert_location_lower.split(",")
        
        # Same city = maximum proximity
        if user_parts[0].strip() == alert_parts[0].strip():
            return 1.0
        
        # Same country = high proximity
        if len(user_parts) > 1 and len(alert_parts) > 1:
            if user_parts[-1].strip() == alert_parts[-1].strip():
                return 0.6
        
        # Different country = low proximity (unless disease is pandemic)
        return 0.1
    
    def _calculate_family_exposure(self, user: UserProfile, alert: HealthAlert) -> float:
        """
        Calculate risk from family members in affected areas
        """
        if not user.family_members or not alert.location:
            return 0.0
        
        alert_location_lower = alert.location.lower()
        alert_parts = alert_location_lower.split(",")
        
        max_exposure = 0.0
        
        for family_member in user.family_members:
            member_location_lower = family_member.location.lower()
            member_parts = member_location_lower.split(",")
            
            # Family in same city as outbreak
            if member_parts[0].strip() == alert_parts[0].strip():
                max_exposure = max(max_exposure, 0.8)
            # Family in same country as outbreak
            elif len(member_parts) > 1 and len(alert_parts) > 1:
                if member_parts[-1].strip() == alert_parts[-1].strip():
                    max_exposure = max(max_exposure, 0.4)
        
        return max_exposure
    
    def _calculate_travel_risk(self, user: UserProfile, alert: HealthAlert) -> float:
        """
        Calculate risk from upcoming travel to affected areas
        """
        if not user.travel_plans or not alert.location:
            return 0.0
        
        alert_location_lower = alert.location.lower()
        alert_parts = alert_location_lower.split(",")
        now = datetime.utcnow()
        
        max_risk = 0.0
        
        for travel in user.travel_plans:
            # Only consider future or current trips
            if travel.return_date < now:
                continue
            
            destination_lower = travel.destination.lower()
            destination_parts = destination_lower.split(",")
            
            # Traveling to affected city
            if destination_parts[0].strip() == alert_parts[0].strip():
                # Imminent travel (within 2 weeks) = highest risk
                days_until_departure = (travel.departure_date - now).days
                if days_until_departure <= 14:
                    max_risk = max(max_risk, 1.0)
                else:
                    max_risk = max(max_risk, 0.7)
            
            # Traveling to affected country
            elif len(destination_parts) > 1 and len(alert_parts) > 1:
                if destination_parts[-1].strip() == alert_parts[-1].strip():
                    max_risk = max(max_risk, 0.5)
        
        return max_risk
    
    def _get_learned_preference(self, user: UserProfile, alert: HealthAlert) -> float:
        """
        Get user's learned preference weight for this type of alert
        
        Uses historical feedback to adjust sensitivity
        """
        # Check if user has learned weights for this disease
        disease_key = alert.disease.lower()
        if disease_key in user.learned_weights:
            return user.learned_weights[disease_key]
        
        # Default: moderate sensitivity
        return 0.5
    
    def _calculate_composite_score(self, factors: RiskFactors, user: UserProfile) -> float:
        """
        Calculate weighted composite risk score
        
        Weights are based on medical research and user preferences
        """
        # Base weights (can be adjusted via learning)
        weights = {
            "base_severity": 0.25,
            "health_vulnerability": 0.25,
            "geographic_proximity": 0.15,
            "family_exposure": 0.15,
            "travel_risk": 0.15,
            "learned_preference": 0.05
        }
        
        composite = (
            factors.base_severity * weights["base_severity"] +
            factors.health_vulnerability * weights["health_vulnerability"] +
            factors.geographic_proximity * weights["geographic_proximity"] +
            factors.family_exposure * weights["family_exposure"] +
            factors.travel_risk * weights["travel_risk"] +
            factors.learned_preference * weights["learned_preference"]
        )
        
        return min(composite, 1.0)
    
    def _classify_risk_level(self, score: float) -> RiskLevel:
        """Classify numeric risk score into categorical risk level"""
        if score >= 0.70:
            return RiskLevel.CRITICAL
        elif score >= 0.50:  # Lowered from 0.60 to catch more HIGH risk
            return RiskLevel.HIGH
        elif score >= 0.35:  # Lowered from 0.40
            return RiskLevel.MEDIUM
        elif score >= 0.20:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _generate_reasoning(
        user: UserProfile, 
        alert: HealthAlert, 
        factors: RiskFactors
    ) -> List[str]:
        """
        Generate human-readable reasoning for the risk assessment
        
        This is crucial for explainability and trust
        """
        reasoning = []
        
        # Base severity
        if factors.base_severity >= 0.7:
            reasoning.append(f"High severity {alert.severity.value} outbreak reported")
        elif factors.base_severity >= 0.4:
            reasoning.append(f"Moderate severity {alert.severity.value} detected")
        
        # Health vulnerability
        if factors.health_vulnerability >= 0.7:
            conditions = [c.name for c in user.health_conditions]
            reasoning.append(f"Your health conditions ({', '.join(conditions)}) increase vulnerability")
        elif factors.health_vulnerability >= 0.4:
            reasoning.append(f"Some of your health conditions may be relevant")
        
        # Geographic proximity
        if factors.geographic_proximity >= 0.9:
            reasoning.append(f"Outbreak is in your current location ({user.location})")
        elif factors.geographic_proximity >= 0.5:
            reasoning.append(f"Outbreak is in your country/region")
        
        # Family exposure
        if factors.family_exposure >= 0.7:
            reasoning.append(f"Family members are in the affected area")
        elif factors.family_exposure >= 0.4:
            reasoning.append(f"Family members may be in nearby regions")
        
        # Travel risk
        if factors.travel_risk >= 0.7:
            reasoning.append(f"You have upcoming travel to the affected area")
        elif factors.travel_risk >= 0.4:
            reasoning.append(f"Your travel plans may be affected")
        
        # Default reasoning if no strong factors
        if not reasoning:
            reasoning.append("Low overall risk based on your profile")
        
        return reasoning
    
    def _determine_actions(self, risk_level: RiskLevel, score: float) -> List[ActionType]:
        """Determine recommended actions based on risk level"""
        actions = []
        
        if risk_level == RiskLevel.CRITICAL:
            actions = [ActionType.IMMEDIATE_ALERT, ActionType.EMAIL_NOTIFICATION]
        elif risk_level == RiskLevel.HIGH:
            actions = [ActionType.EMAIL_NOTIFICATION]
        elif risk_level == RiskLevel.MEDIUM:
            actions = [ActionType.LOG_ONLY]
        else:  # LOW or MINIMAL
            actions = [ActionType.LOG_ONLY]
        
        return actions
    
    def _calculate_priority(self, score: float) -> int:
        """Calculate notification priority (1-10, lower = higher priority)"""
        # Invert score: higher risk = lower priority number = higher priority
        return max(1, min(10, int((1.0 - score) * 10) + 1))
    
    def _calculate_confidence(self, user: UserProfile, alert: HealthAlert) -> float:
        """
        Calculate confidence in the risk assessment based on data completeness
        """
        confidence_factors = []
        
        # User profile completeness
        if user.health_conditions:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.5)
        
        if user.family_members:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.8)
        
        if user.travel_plans:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.9)
        
        # Alert data completeness
        if alert.latitude and alert.longitude:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.7)
        
        if alert.mortality_rate:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.8)
        
        # Average confidence
        return sum(confidence_factors) / len(confidence_factors)
    
    def _default_medical_knowledge(self) -> Dict[str, Dict[str, float]]:
        """
        Default medical knowledge base: disease → condition → risk multiplier
        
        In production: load from database or medical API
        For MVP: hard-coded common interactions
        """
        return {
            "dengue": {
                "diabetes": 2.5,
                "heart disease": 2.0,
                "hypertension": 1.8,
                "pregnancy": 3.0,
                "kidney disease": 2.3,
                "asthma": 1.3,
            },
            "covid-19": {
                "diabetes": 2.2,
                "heart disease": 2.5,
                "hypertension": 2.0,
                "obesity": 1.9,
                "copd": 2.8,
                "cancer": 2.4,
                "pregnancy": 1.7,
            },
            "flu": {
                "asthma": 2.5,
                "copd": 2.8,
                "pregnancy": 2.0,
                "heart disease": 1.8,
                "diabetes": 1.6,
            },
            "measles": {
                "immunocompromised": 3.0,
                "pregnancy": 2.5,
                "malnutrition": 2.2,
            },
            "malaria": {
                "pregnancy": 3.0,
                "hiv/aids": 2.5,
                "sickle cell disease": 2.8,
            },
        }


# Global instance
risk_calculator = RiskCalculator()
