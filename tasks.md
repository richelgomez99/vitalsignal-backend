# VitalSignal Task Tracker

**Last Updated:** 2025-10-04 11:27 AM
**Time Remaining:** ~4.5 hours

---

## Phase 1: Core API Development ⏰ 90 min

### Project Setup
- [x] Create project structure
- [x] Initialize git repository
- [x] Create .gitignore
- [x] Create .env with API keys
- [x] Create .env.example template
- [x] Create README.md
- [x] Create plan.md
- [x] Create tasks.md
- [x] Create requirements.txt
- [x] Setup guides (AIRIA_SETUP_GUIDE.md, NGROK_SETUP_GUIDE.md)
- [ ] Install dependencies (USER ACTION NEEDED)

### Database Schema
- [x] Design ClickHouse schema (users, alerts, feedback)
- [x] Create schema initialization script (scripts/init_db.py)
- [ ] Test ClickHouse connection (USER ACTION NEEDED)
- [ ] Seed demo users (Maria, John, Sarah) (USER ACTION NEEDED)

### Core Models
- [x] Create src/__init__.py
- [x] Create src/models.py (Pydantic models)
  - [x] UserProfile model
  - [x] HealthAlert model
  - [x] RiskScore model
  - [x] FeedbackEvent model
- [x] Create src/config.py (env var management)

### Risk Calculator (CRITICAL)
- [x] Create src/risk_calculator.py
  - [x] Calculate base severity score
  - [x] Factor in user health conditions
  - [x] Factor in geographic relevance
  - [x] Factor in family connections
  - [x] Factor in travel plans
  - [x] Factor in user preferences
  - [x] Generate action recommendation
  - [x] Generate reasoning (explainability)
  - [x] Confidence scoring
  - [x] Medical knowledge base
- [x] Test script for risk calculator (scripts/test_api.py)

### Main API
- [x] Create src/main.py (FastAPI app)
- [x] Add health check endpoint
- [x] Add /api/v1/personalize endpoint (CORE)
- [x] Add /api/v1/users endpoints (GET, POST)
- [x] Add /api/v1/feedback endpoint
- [x] Add /api/v1/metrics endpoint
- [x] CORS middleware for Airia
- [x] Error handling
- [ ] Test locally (USER ACTION NEEDED)

---

## Phase 2: External Integrations ⏰ 75 min

### Structify (Alert Scraping)
- [ ] Create src/utils/structify_client.py
- [ ] Test API authentication
- [ ] Implement scrape_health_alerts()
- [ ] Mock data fallback

### PhenoML (Medical Enrichment)
- [ ] Create src/fhir_transformer.py
- [ ] Get auth token from API
- [ ] Implement enrich_with_medical_codes()
- [ ] Parse FHIR response

### DeepL (Translation)
- [ ] Create src/utils/deepl_client.py
- [ ] Test API key
- [ ] Implement translate_alert()
- [ ] Language detection logic

### Freepik (Image Generation)
- [ ] Create src/utils/freepik_client.py
- [ ] Test API key
- [ ] Implement generate_alert_image()
- [ ] Handle async job polling

### SendGrid (Email Notifications)
- [ ] Create src/utils/sendgrid_client.py
- [ ] Test API key
- [ ] Create email template
- [ ] Implement send_alert_email()
- [ ] Test with richel.gomez@pursuit.org

### ClickHouse (Database)
- [x] Create src/utils/clickhouse_client.py
- [x] Implement get_user()
- [x] Implement create_user()
- [x] Implement get_all_users()
- [x] Implement save_alert()
- [x] Implement save_risk_assessment()
- [x] Implement save_feedback()
- [x] Implement get_metrics()
- [x] Implement log_api_call()

---

## Phase 3: Intelligence Layer ⏰ 60 min

### Medical Knowledge
- [ ] Create src/utils/medical_knowledge.py
- [ ] Define disease-condition interaction matrix
- [ ] Implement get_risk_multiplier()
- [ ] Add common conditions (diabetes, pregnancy, etc.)

### Learning Engine
- [ ] Create src/learning_engine.py
- [ ] Implement record_feedback()
- [ ] Implement adjust_user_preferences()
- [ ] Implement get_learned_weights()
- [ ] Simple ML model or rule-based adaptation

### Enhanced Risk Scoring
- [ ] Integrate medical knowledge into risk calculator
- [ ] Add learning weight adjustments
- [ ] Add reasoning explanation generation
- [ ] Add confidence scores

---

## Phase 4: Demo Preparation ⏰ 60 min

### Demo Data
- [ ] Create demo/seed_data.json
- [ ] User 1: Maria (diabetic, sister in São Paulo)
- [ ] User 2: John (healthy, no connections)
- [ ] User 3: Sarah (pregnant, travel to Brazil)
- [ ] Sample alert: Dengue in São Paulo

### Demo Dashboard
- [ ] Create demo/index.html
- [ ] Three-column layout (3 users side-by-side)
- [ ] Add CSS styling
- [ ] Add JavaScript for API calls
- [ ] Show risk scores + reasoning + actions

### Testing
- [ ] Test all 3 user scenarios
- [ ] Verify different outcomes
- [ ] Test external API integrations
- [ ] Check error handling
- [ ] Performance check

### Presentation
- [ ] Write 3-minute demo script
- [ ] Prepare talking points
- [ ] Screenshot for backup
- [ ] Test demo flow timing

---

## Phase 5: Deployment + Buffer ⏰ 45 min

### Deployment
- [ ] Create Dockerfile (optional)
- [ ] Test ngrok tunnel
- [ ] OR deploy to Railway/Render
- [ ] Update CORS settings
- [ ] Test from external device

### Final Checks
- [ ] All endpoints responding
- [ ] Demo runs smoothly
- [ ] GitHub repo pushed
- [ ] DevPost submission ready
- [ ] Demo URL accessible

### Documentation
- [ ] Update README with demo URL
- [ ] Add architecture diagram
- [ ] Document API endpoints
- [ ] Add setup instructions

---

## Completed Tasks ✅

*(Tasks will move here as completed)*

---

## Blocked/Issues 🚫

*(No blockers yet - will track in issues.md if any arise)*

---

## Notes

- **Priority:** Phase 1 → Phase 3 → Phase 4 (risk calculator is the core)
- **If short on time:** Mock external APIs, focus on risk scoring logic
- **Time buffers:** Built into each phase for debugging
