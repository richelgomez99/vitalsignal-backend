# VitalSignal: Personal Health Guardian AI Agent

**Hackathon Project** - Autonomous AI agent for personalized disease outbreak monitoring

## Concept

VitalSignal monitors global disease outbreaks and makes **PERSONALIZED** decisions about what matters to each user based on:
- Health profile (conditions, medications, allergies)
- Family member locations
- Travel plans
- Risk tolerance preferences

**Key Differentiator:** Same alert → 3 different outcomes. Non-deterministic, adaptive behavior.

## Architecture

```
Airia (Orchestration)
    ↓
Custom FastAPI Microservices (Intelligence)
    ├── Personalization Engine - Risk scoring & decision logic
    ├── FHIR Transformer - Medical data enrichment
    └── Learning Engine - Behavioral adaptation
    ↓
External Tools (6)
    ├── Structify - Web scraping health alerts
    ├── PhenoML - Medical code enrichment (FHIR/SNOMED/ICD-10)
    ├── DeepL - Conditional translation
    ├── Freepik - Severity-based image generation
    ├── ClickHouse - User profiles + learning data
    └── SendGrid - Personalized notifications
```

## Why This Wins Autonomy

1. **Multi-factor decision making** - 8+ variables per alert
2. **User-specific outcomes** - Different users, different actions
3. **Continuous learning** - Adapts from user feedback
4. **Proactive intelligence** - Anticipates needs (travel, family)
5. **Non-deterministic** - Real reasoning, not workflows

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database schema
python scripts/init_db.py

# Run server
uvicorn src.main:app --reload --port 8000
```

## API Endpoints

### Core Intelligence
- `POST /api/v1/personalize` - Calculate personalized risk score
- `POST /api/v1/enrich` - Transform to FHIR-compatible format
- `POST /api/v1/learn` - Record user feedback for learning

### User Management
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user profile
- `GET /api/v1/users/{id}` - Get user details

### Health Checks
- `GET /health` - Service health
- `GET /metrics` - Decision metrics

## Demo Flow

1. **Alert arrives** - E.g., "Dengue outbreak in São Paulo"
2. **Three users, three outcomes:**
   - **Maria** (diabetic, sister in SP) → HIGH ALERT + image + translation
   - **John** (healthy, no connections) → Low priority, logged only
   - **Sarah** (pregnant, flying to Brazil next week) → CRITICAL + travel advisory

## Tech Stack

- **FastAPI** - API framework
- **Pydantic** - Data validation
- **ClickHouse** - Time-series health data
- **HTTPX** - Async HTTP client
- **Python 3.11+**

## Deployment

**Option A:** Local + ngrok (current)
```bash
ngrok http 8000
```

**Option B:** Cloud deployment (post-hackathon)
- Dockerfile included
- Deploy to Railway/Render
- Environment variables via platform

## Judging Criteria Alignment

| Criterion | How We Address |
|-----------|---------------|
| **Autonomy (20%)** | Multi-factor reasoning, non-deterministic outcomes, learning from feedback |
| **Idea (20%)** | Real-world health personalization, addresses alert fatigue |
| **Technical (20%)** | Custom ML logic, FHIR integration, real API implementations |
| **Tool Use (20%)** | 6 sponsor tools integrated |
| **Presentation (20%)** | Live demo with 3 users side-by-side |

## Team

Richel Gomez - richel.gomez@pursuit.org

## License

MIT (Hackathon Project)
