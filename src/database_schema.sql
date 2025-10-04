-- VitalSignal ClickHouse Database Schema
-- Time-series optimized for health alerts and user interactions

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id String,
    email String,
    name String,
    age UInt8,
    location String,
    latitude Nullable(Float64),
    longitude Nullable(Float64),
    
    -- Health information (JSON strings)
    health_conditions String,  -- JSON array
    medications String,         -- JSON array
    allergies String,           -- JSON array
    
    -- Context (JSON strings)
    family_members String,      -- JSON array
    travel_plans String,        -- JSON array
    
    -- Preferences (JSON string)
    preferences String,         -- JSON object
    
    -- Learning data (JSON string)
    learned_weights String,     -- JSON object
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (user_id, created_at);

-- Health alerts table
CREATE TABLE IF NOT EXISTS health_alerts (
    alert_id String,
    title String,
    description String,
    disease String,
    location String,
    latitude Nullable(Float64),
    longitude Nullable(Float64),
    
    severity String,  -- pandemic, epidemic, outbreak, cluster, sporadic
    affected_population Nullable(UInt32),
    mortality_rate Nullable(Float64),
    
    source String,
    source_url Nullable(String),
    
    -- Medical codes (JSON strings)
    icd10_codes String,     -- JSON array
    snomed_codes String,    -- JSON array
    fhir_data String,       -- JSON object
    
    published_at DateTime,
    scraped_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (disease, published_at);

-- Risk assessments table (time-series)
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id String,
    user_id String,
    alert_id String,
    
    risk_level String,  -- critical, high, medium, low, minimal
    risk_score Float64,
    confidence Float64,
    
    -- Risk factors breakdown
    base_severity Float64,
    health_vulnerability Float64,
    geographic_proximity Float64,
    family_exposure Float64,
    travel_risk Float64,
    learned_preference Float64,
    
    -- Actions
    recommended_actions String,  -- JSON array
    needs_translation Bool,
    needs_image Bool,
    priority UInt8,
    
    -- Reasoning
    reasoning String,  -- JSON array of strings
    
    -- Metadata
    processing_time_ms Float64,
    external_apis_called String,  -- JSON array
    
    calculated_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(calculated_at)
ORDER BY (user_id, calculated_at);

-- Feedback events table (for learning)
CREATE TABLE IF NOT EXISTS feedback_events (
    feedback_id String,
    user_id String,
    alert_id String,
    
    feedback_type String,  -- helpful, not_helpful, too_sensitive, etc.
    user_comment Nullable(String),
    
    -- Original assessment for learning
    original_risk_score Float64,
    original_risk_level String,
    
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (user_id, created_at);

-- External API call logs (for monitoring)
CREATE TABLE IF NOT EXISTS api_call_logs (
    call_id String,
    service_name String,  -- structify, phenoml, deepl, freepik, sendgrid
    endpoint String,
    http_method String,
    
    status_code UInt16,
    response_time_ms Float64,
    success Bool,
    error_message Nullable(String),
    
    -- Context
    user_id Nullable(String),
    alert_id Nullable(String),
    
    called_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (service_name, called_at);

-- Materialized view for metrics (optional, for demo)
CREATE MATERIALIZED VIEW IF NOT EXISTS risk_assessment_metrics
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, risk_level)
AS SELECT
    toDate(calculated_at) as date,
    risk_level,
    count() as assessment_count,
    avg(risk_score) as avg_risk_score,
    avg(processing_time_ms) as avg_processing_time
FROM risk_assessments
GROUP BY date, risk_level;
