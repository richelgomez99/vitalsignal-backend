#!/usr/bin/env python3
"""Quick script to add demo users directly to database"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import json

from src.utils.clickhouse_client import db_client
from src.models import UserProfile, HealthCondition, FamilyMember, TravelPlan, UserPreferences

# User 1: Maria (Diabetic + Family in Brazil)
maria = UserProfile(
    user_id="demo_maria",
    email="maria.silva@example.com",
    name="Maria Silva",
    age=45,
    location="New York, USA",
    health_conditions=[
        HealthCondition(name="diabetes", severity="moderate")
    ],
    family_members=[
        FamilyMember(name="Ana Silva", relationship="sister", location="São Paulo, Brazil")
    ],
    preferences=UserPreferences()
)

# User 2: John (Healthy)
john = UserProfile(
    user_id="demo_john",
    email="john.smith@example.com",
    name="John Smith",
    age=32,
    location="Seattle, USA",
    health_conditions=[],
    family_members=[],
    preferences=UserPreferences()
)

# User 3: Sarah (Pregnant + Traveling)
sarah = UserProfile(
    user_id="demo_sarah",
    email="sarah.johnson@example.com",
    name="Sarah Johnson",
    age=29,
    location="Miami, USA",
    health_conditions=[
        HealthCondition(name="pregnancy", severity="moderate")
    ],
    travel_plans=[
        TravelPlan(
            destination="São Paulo, Brazil",
            departure_date=datetime(2025, 10, 14, 10, 0, 0),
            return_date=datetime(2025, 10, 21, 18, 0, 0),
            purpose="vacation"
        )
    ],
    preferences=UserPreferences()
)

print("Adding demo users...")

try:
    # Try to create users
    for user in [maria, john, sarah]:
        success = db_client.create_user(user)
        if success:
            print(f"✅ Created {user.name} ({user.user_id})")
        else:
            print(f"❌ Failed to create {user.name}")
    
    # Verify
    print("\nVerifying users...")
    users = db_client.get_all_users()
    print(f"Total users in database: {len(users)}")
    for u in users:
        print(f"  - {u.name} ({u.user_id})")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
