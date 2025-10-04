"""
Quick API Test Script

Tests the core personalization endpoint with demo users
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import HealthAlert, DiseaseSeverity, PersonalizationRequest
from src.risk_calculator import risk_calculator
from src.utils.clickhouse_client import db_client


def create_sample_alert():
    """Create a sample dengue alert for São Paulo"""
    return HealthAlert(
        alert_id="test_dengue_sp_001",
        title="Dengue Outbreak in São Paulo",
        description="Health authorities report a significant increase in dengue fever cases in São Paulo, Brazil. Over 500 confirmed cases in the past week, with 3 fatalities.",
        disease="dengue",
        location="São Paulo, Brazil",
        latitude=-23.5505,
        longitude=-46.6333,
        severity=DiseaseSeverity.OUTBREAK,
        affected_population=500,
        mortality_rate=0.6,  # 0.6%
        source="WHO",
        source_url="https://www.who.int/emergencies/disease-outbreak-news",
        published_at=datetime.utcnow()
    )


def test_personalization():
    """Test personalization for all demo users"""
    print("=" * 70)
    print("VitalSignal Risk Calculator Test")
    print("=" * 70)
    print()
    
    # Create sample alert
    alert = create_sample_alert()
    print(f"📢 Alert: {alert.title}")
    print(f"   Location: {alert.location}")
    print(f"   Severity: {alert.severity.value}")
    print(f"   Disease: {alert.disease}")
    print()
    print("=" * 70)
    print()
    
    # Get all demo users
    users = db_client.get_all_users()
    
    if not users:
        print("❌ No users found. Run 'python scripts/init_db.py' first.")
        return
    
    # Test each user
    for i, user in enumerate(users, 1):
        print(f"👤 User {i}: {user.name} ({user.user_id})")
        print(f"   Age: {user.age}, Location: {user.location}")
        print(f"   Health conditions: {[c.name for c in user.health_conditions] or 'None'}")
        print(f"   Family members: {len(user.family_members)}")
        print(f"   Travel plans: {len(user.travel_plans)}")
        print()
        
        # Calculate risk
        risk_score = risk_calculator.calculate_risk(user, alert)
        
        # Display results
        print(f"   🎯 RISK ASSESSMENT:")
        print(f"      Risk Level: {risk_score.risk_level.value.upper()}")
        print(f"      Risk Score: {risk_score.risk_score:.2f} (0-1 scale)")
        print(f"      Confidence: {risk_score.confidence:.2f}")
        print()
        
        print(f"   📊 Risk Factors:")
        print(f"      Base Severity: {risk_score.risk_factors.base_severity:.2f}")
        print(f"      Health Vulnerability: {risk_score.risk_factors.health_vulnerability:.2f}")
        print(f"      Geographic Proximity: {risk_score.risk_factors.geographic_proximity:.2f}")
        print(f"      Family Exposure: {risk_score.risk_factors.family_exposure:.2f}")
        print(f"      Travel Risk: {risk_score.risk_factors.travel_risk:.2f}")
        print()
        
        print(f"   💭 Reasoning:")
        for reason in risk_score.reasoning:
            print(f"      • {reason}")
        print()
        
        print(f"   ⚡ Recommended Actions:")
        for action in risk_score.recommended_actions:
            print(f"      • {action.value}")
        print()
        
        print(f"   🔔 Notifications:")
        print(f"      Priority: {risk_score.priority}/10")
        print(f"      Needs Translation: {risk_score.needs_translation}")
        print(f"      Needs Image: {risk_score.needs_image}")
        print()
        
        print("-" * 70)
        print()
    
    print("=" * 70)
    print("✅ Test complete!")
    print()
    print("🎯 Expected Outcomes:")
    print("   • Maria → HIGH risk (diabetic + family in SP)")
    print("   • John → LOW risk (healthy + no connections)")
    print("   • Sarah → CRITICAL risk (pregnant + traveling to SP)")
    print("=" * 70)


def main():
    """Main test"""
    # Check database connection
    if not db_client.health_check():
        print("❌ Cannot connect to database.")
        print("   Make sure ClickHouse is configured in .env")
        print("   Run: python scripts/init_db.py")
        sys.exit(1)
    
    test_personalization()


if __name__ == "__main__":
    main()
