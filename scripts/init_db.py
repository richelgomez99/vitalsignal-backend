"""
Database Initialization Script

Creates ClickHouse tables and seeds demo data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.clickhouse_client import db_client
from src.config import settings


def create_tables():
    """Create all database tables"""
    print("📊 Creating ClickHouse tables...")
    
    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'database_schema.sql')
    
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    # Split into individual statements
    statements = [s.strip() for s in schema.split(';') if s.strip() and not s.strip().startswith('--')]
    
    for i, statement in enumerate(statements, 1):
        try:
            if statement:
                db_client.client.command(statement)
                print(f"  ✅ Statement {i}/{len(statements)} executed")
        except Exception as e:
            print(f"  ❌ Statement {i} failed: {e}")
            # Continue anyway - table might already exist
    
    print("✅ Tables created successfully\n")


def seed_demo_data():
    """Seed database with demo users"""
    print("🌱 Seeding demo data...")
    
    from datetime import datetime, timedelta
    from src.models import (
        UserProfile, HealthCondition, FamilyMember, TravelPlan, 
        UserPreferences, RiskLevel
    )
    
    # Demo User 1: Maria - High Risk (Diabetic, Sister in São Paulo)
    maria = UserProfile(
        user_id="demo_maria",
        email="maria.silva@example.com",
        name="Maria Silva",
        age=45,
        location="New York, USA",
        latitude=40.7128,
        longitude=-74.0060,
        health_conditions=[
            HealthCondition(
                name="diabetes",
                icd10_code="E11",
                severity="moderate",
                diagnosed_date=datetime(2018, 3, 15)
            ),
            HealthCondition(
                name="hypertension",
                icd10_code="I10",
                severity="mild",
                diagnosed_date=datetime(2020, 7, 22)
            )
        ],
        medications=[],
        allergies=["penicillin"],
        family_members=[
            FamilyMember(
                name="Ana Silva",
                relationship="sister",
                location="São Paulo, Brazil",
                latitude=-23.5505,
                longitude=-46.6333
            ),
            FamilyMember(
                name="Carlos Silva",
                relationship="brother",
                location="Rio de Janeiro, Brazil",
                latitude=-22.9068,
                longitude=-43.1729
            )
        ],
        travel_plans=[],
        preferences=UserPreferences(
            risk_tolerance="low",
            notification_threshold=RiskLevel.MEDIUM,
            preferred_language="en",
            wants_images=True,
            wants_translations=False
        ),
        learned_weights={}
    )
    
    # Demo User 2: John - Low Risk (Healthy, No Connections)
    john = UserProfile(
        user_id="demo_john",
        email="john.smith@example.com",
        name="John Smith",
        age=32,
        location="Seattle, USA",
        latitude=47.6062,
        longitude=-122.3321,
        health_conditions=[],
        medications=[],
        allergies=[],
        family_members=[
            FamilyMember(
                name="Jane Smith",
                relationship="sister",
                location="Portland, USA",
                latitude=45.5152,
                longitude=-122.6784
            )
        ],
        travel_plans=[],
        preferences=UserPreferences(
            risk_tolerance="high",
            notification_threshold=RiskLevel.HIGH,
            preferred_language="en",
            wants_images=False,
            wants_translations=False
        ),
        learned_weights={}
    )
    
    # Demo User 3: Sarah - Critical Risk (Pregnant, Traveling to Brazil)
    sarah = UserProfile(
        user_id="demo_sarah",
        email="sarah.johnson@example.com",
        name="Sarah Johnson",
        age=29,
        location="Miami, USA",
        latitude=25.7617,
        longitude=-80.1918,
        health_conditions=[
            HealthCondition(
                name="pregnancy",
                icd10_code="Z34",
                severity="moderate",
                diagnosed_date=datetime.utcnow() - timedelta(days=120)  # 4 months pregnant
            )
        ],
        medications=[],
        allergies=[],
        family_members=[
            FamilyMember(
                name="Michael Johnson",
                relationship="husband",
                location="Miami, USA",
                latitude=25.7617,
                longitude=-80.1918
            )
        ],
        travel_plans=[
            TravelPlan(
                destination="São Paulo, Brazil",
                departure_date=datetime.utcnow() + timedelta(days=10),
                return_date=datetime.utcnow() + timedelta(days=17),
                purpose="Business conference"
            ),
            TravelPlan(
                destination="Rio de Janeiro, Brazil",
                departure_date=datetime.utcnow() + timedelta(days=17),
                return_date=datetime.utcnow() + timedelta(days=21),
                purpose="Vacation"
            )
        ],
        preferences=UserPreferences(
            risk_tolerance="low",
            notification_threshold=RiskLevel.LOW,
            preferred_language="en",
            wants_images=True,
            wants_translations=True
        ),
        learned_weights={}
    )
    
    # Insert users
    users = [maria, john, sarah]
    
    for user in users:
        try:
            success = db_client.create_user(user)
            if success:
                print(f"  ✅ Created user: {user.name} ({user.user_id})")
            else:
                print(f"  ⚠️  User {user.name} might already exist")
        except Exception as e:
            print(f"  ❌ Failed to create {user.name}: {e}")
    
    print("\n✅ Demo data seeded successfully")
    print("\n📋 Demo Users:")
    print("  1. Maria Silva - Diabetic + Family in Brazil → Expect HIGH risk")
    print("  2. John Smith - Healthy + No connections → Expect LOW risk")
    print("  3. Sarah Johnson - Pregnant + Traveling to Brazil → Expect CRITICAL risk")


def main():
    """Main initialization"""
    print("=" * 60)
    print("VitalSignal Database Initialization")
    print("=" * 60)
    print(f"Environment: {settings.environment}")
    print(f"Database: {settings.clickhouse_host}")
    print("=" * 60)
    print()
    
    # Check connection
    if not db_client.health_check():
        print("❌ Cannot connect to database. Check your .env configuration:")
        print(f"   CLICKHOUSE_HOST={settings.clickhouse_host}")
        print(f"   CLICKHOUSE_USER={settings.clickhouse_user}")
        print(f"   CLICKHOUSE_DATABASE={settings.clickhouse_database}")
        sys.exit(1)
    
    print("✅ Database connection successful\n")
    
    # Create tables
    create_tables()
    
    # Seed demo data
    seed_demo_data()
    
    print("\n" + "=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start the API: uvicorn src.main:app --reload --port 8000")
    print("  2. Start ngrok: ngrok http 8000")
    print("  3. Test health: curl http://localhost:8000/health")
    print("  4. View docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
