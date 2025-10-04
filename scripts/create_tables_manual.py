#!/usr/bin/env python3
"""Manually create ClickHouse tables one by one"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.clickhouse_client import db_client

# Individual CREATE TABLE statements
tables = {
    "users": """
CREATE TABLE IF NOT EXISTS users (
    user_id String,
    email String,
    name String,
    age UInt8,
    location String,
    latitude Nullable(Float64),
    longitude Nullable(Float64),
    health_conditions String,
    medications String,
    allergies String,
    family_members String,
    travel_plans String,
    preferences String,
    learned_weights String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (user_id, created_at)
""",
    
    "health_alerts": """
CREATE TABLE IF NOT EXISTS health_alerts (
    alert_id String,
    title String,
    description String,
    disease String,
    location String,
    latitude Nullable(Float64),
    longitude Nullable(Float64),
    severity String,
    affected_population Nullable(UInt32),
    mortality_rate Nullable(Float64),
    source String,
    source_url Nullable(String),
    icd10_codes String,
    snomed_codes String,
    fhir_data String,
    published_at DateTime,
    scraped_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (disease, published_at)
""",
    
    "risk_assessments": """
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id String,
    user_id String,
    alert_id String,
    risk_level String,
    risk_score Float64,
    confidence Float64,
    base_severity Float64,
    health_vulnerability Float64,
    geographic_proximity Float64,
    family_exposure Float64,
    travel_risk Float64,
    learned_preference Float64,
    recommended_actions String,
    needs_translation Bool,
    needs_image Bool,
    priority UInt8,
    reasoning String,
    processing_time_ms Float64,
    external_apis_called String,
    calculated_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(calculated_at)
ORDER BY (user_id, calculated_at)
""",
    
    "feedback_events": """
CREATE TABLE IF NOT EXISTS feedback_events (
    feedback_id String,
    user_id String,
    alert_id String,
    feedback_type String,
    user_comment Nullable(String),
    original_risk_score Float64,
    original_risk_level String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (user_id, created_at)
"""
}

print("Creating ClickHouse tables...\n")

for table_name, sql in tables.items():
    try:
        print(f"Creating table: {table_name}")
        db_client.client.command(sql)
        print(f"  ✅ {table_name} created successfully\n")
    except Exception as e:
        print(f"  ❌ Failed: {e}\n")

# Verify tables exist
print("Verifying tables...")
try:
    result = db_client.client.query("SHOW TABLES")
    tables_list = [row[0] for row in result.result_rows]
    print(f"Tables in database: {tables_list}")
except Exception as e:
    print(f"Error checking tables: {e}")
