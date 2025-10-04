#!/usr/bin/env python3
"""Add high-risk demo users to trigger different risk levels"""

import asyncio
from datetime import datetime, timedelta
from src.utils.clickhouse_client import db_client
from src.models import UserProfile, HealthCondition, FamilyMember, TravelPlan, UserPreferences


async def add_high_risk_users():
    """Add 3 users designed to trigger HIGH/CRITICAL risks"""
    
    # User 3: Pregnant woman traveling to Brazil (CRITICAL for Dengue)
    user3 = UserProfile(
        user_id="demo_sarah",
        email="sarah.chen@example.com",
        name="Sarah Chen",
        age=28,
        location="Los Angeles, USA",
        health_conditions=[
            HealthCondition(
                name="pregnancy",
                severity="high",
                diagnosed_date=datetime.utcnow() - timedelta(days=120)
            )
        ],
        travel_plans=[
            TravelPlan(
                destination="Rio de Janeiro, Brazil",
                departure_date=datetime.utcnow() + timedelta(days=14),
                return_date=datetime.utcnow() + timedelta(days=28),
                purpose="vacation"
            )
        ],
        preferences=UserPreferences(
            risk_tolerance="low",
            notification_threshold="low",
            preferred_language="en"
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # User 4: Healthcare worker in Africa (HIGH for Mpox + Marburg)
    user4 = UserProfile(
        user_id="demo_kwame",
        email="kwame.osei@example.com",
        name="Kwame Osei",
        age=35,
        location="Nairobi, Kenya",
        health_conditions=[],
        family_members=[
            FamilyMember(
                name="Amara Osei",
                relationship="sister",
                location="Kigali, Rwanda"
            )
        ],
        travel_plans=[
            TravelPlan(
                destination="Kampala, Uganda",
                departure_date=datetime.utcnow() + timedelta(days=7),
                return_date=datetime.utcnow() + timedelta(days=21),
                purpose="work"
            )
        ],
        preferences=UserPreferences(
            risk_tolerance="moderate",
            notification_threshold="medium",
            preferred_language="en"
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # User 5: Immunocompromised person in Ethiopia (CRITICAL for Malaria)
    user5 = UserProfile(
        user_id="demo_aisha",
        email="aisha.hassan@example.com",
        name="Aisha Hassan",
        age=42,
        location="Addis Ababa, Ethiopia",
        health_conditions=[
            HealthCondition(
                name="hiv",
                severity="high",
                diagnosed_date=datetime.utcnow() - timedelta(days=730)
            ),
            HealthCondition(
                name="immunosuppression",
                severity="high",
                diagnosed_date=datetime.utcnow() - timedelta(days=365)
            )
        ],
        preferences=UserPreferences(
            risk_tolerance="low",
            notification_threshold="low",
            preferred_language="en"
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Insert users
    print("Adding high-risk demo users...")
    
    users = [user3, user4, user5]
    
    for user in users:
        try:
            db_client.create_user(user)
            print(f"✅ Added: {user.name} ({user.user_id})")
        except Exception as e:
            print(f"⚠️  {user.name}: {e}")
    
    print("\n✅ All high-risk users added!")
    print("\nExpected outcomes:")
    print("- Sarah Chen (demo_sarah): CRITICAL for Dengue (pregnant + traveling to Brazil)")
    print("- Kwame Osei (demo_kwame): HIGH for Marburg (sister in Rwanda) + Mpox (Africa location)")
    print("- Aisha Hassan (demo_aisha): CRITICAL for Malaria (immunocompromised + IN Ethiopia)")


if __name__ == "__main__":
    asyncio.run(add_high_risk_users())
