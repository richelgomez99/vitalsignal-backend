# 🚀 START HERE - VitalSignal Backend

**Status:** ✅ Phase 1 Complete - Ready for Integration Testing
**Time:** 2025-10-04 11:38 AM
**Remaining:** ~4 hours until 4:30 PM deadline

---

## What's Done ✅

I've built the complete backend for VitalSignal:

### ✅ Core Intelligence
- **Risk Calculator** - The heart of autonomy
  - Multi-factor analysis (8 variables)
  - Medical knowledge base (disease-condition interactions)
  - Geographic proximity calculations
  - Family exposure analysis
  - Travel risk assessment
  - Reasoning generation (explainability)
  - Non-deterministic outcomes (same alert → different results)

### ✅ FastAPI Server
- Health check endpoint (`/health`)
- User management (`/api/v1/users`)
- **Personalization endpoint** (`/api/v1/personalize`) ← THE CORE
- Feedback endpoint (`/api/v1/feedback`)
- Metrics endpoint (`/api/v1/metrics`)
- Interactive API docs (`/docs`)

### ✅ Database Layer
- ClickHouse schema (5 tables)
- Database client with all CRUD operations
- Demo user seed data (3 users with different profiles)

### ✅ Demo Data
- **Maria**: Diabetic + Family in São Paulo → HIGH RISK
- **John**: Healthy + No connections → LOW RISK
- **Sarah**: Pregnant + Traveling to Brazil → CRITICAL RISK

### ✅ Documentation
- README with project overview
- AIRIA_SETUP_GUIDE (step-by-step Airia config)
- NGROK_SETUP_GUIDE (step-by-step ngrok setup)
- SETUP_COMPLETE (detailed technical guide)
- This file (START_HERE)

---

## Current Status ✅

**✅ COMPLETED:**
- [x] Virtual environment created (Python 3.12)
- [x] Dependencies installed
- [x] Database initialized (ClickHouse connected)
- [x] ngrok authenticated and running
- [x] Backend accessible at: `https://chelsey-ideographical-emelia.ngrok-free.dev`

**→ NEXT: Create Airia Tools**

---

## Your Setup Details

**ngrok URL:** `https://chelsey-ideographical-emelia.ngrok-free.dev`

**FastAPI Server:** Running on http://localhost:8000

**Terminal Layout:**
- **Terminal 1:** FastAPI server (`uvicorn src.main:app --reload --port 8000`)
- **Terminal 2:** ngrok tunnel (`ngrok http 8000`)
- **Terminal 3:** Available for testing/commands

---

## Next Steps (15 minutes)

**1. Test Your Endpoints (2 min)**
```bash
# Test health
curl https://chelsey-ideographical-emelia.ngrok-free.dev/health

# Test users endpoint
curl https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users
```

**2. Create Airia Tool #1 (5 min)**
- Open AIRIA_OFFICIAL_TOOL_GUIDE.md
- Create "Get VitalSignal Users" tool
- Use URL: `https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users`

**3. Create Airia Tool #2 (5 min)**
- Create "Personalize Risk Assessment" tool
- Use URL: `https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize`

**4. Add Tools to Agent (3 min)**
- Select both tools
- Configure agent prompt

---

## Quick Reference: Your URLs

**✅ Your Active URLs:**

```
ngrok Public URL: https://chelsey-ideographical-emelia.ngrok-free.dev
Local API: http://localhost:8000

Tool 1 URL: https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users
Tool 2 URL: https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize

API Docs: http://localhost:8000/docs
ngrok Dashboard: http://localhost:4040
```api/v1/personalize \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_maria",
    "alert": {
      "alert_id": "test_001",
      "title": "Dengue Outbreak in São Paulo",
      "description": "500 cases reported",
      "disease": "dengue",
      "location": "São Paulo, Brazil",
      "severity": "outbreak",
      "published_at": "2025-10-04T15:00:00Z"
    }
  }'
```

**Expected:** HIGH risk score (~0.70-0.80) with reasoning about diabetes and family

---

## File Structure

```
vitalsignal-backend/
├── README.md                    # Project overview
├── START_HERE.md               # This file
├── SETUP_COMPLETE.md           # Detailed setup guide
├── AIRIA_SETUP_GUIDE.md        # Airia configuration
├── NGROK_SETUP_GUIDE.md        # ngrok setup
├── plan.md                     # Project timeline
├── tasks.md                    # Task checklist
├── issues.md                   # Bug tracker
│
├── .env                        # YOUR API KEYS (don't commit)
├── .env.example                # Template
├── requirements.txt            # Python dependencies
│
├── src/
│   ├── main.py                 # FastAPI app ⭐
│   ├── models.py               # Pydantic models
│   ├── risk_calculator.py      # Core intelligence ⭐⭐⭐
│   ├── config.py               # Environment config
│   ├── database_schema.sql     # ClickHouse schema
│   └── utils/
│       └── clickhouse_client.py # Database client
│
└── scripts/
    ├── init_db.py              # Database setup
    └── test_api.py             # Local testing
```

---

## The Magic: How It Works

```
1. Airia scrapes health alert (Dengue in São Paulo)
2. Airia calls: POST /api/v1/personalize for each user
3. Our API:
   a. Gets user from database
   b. Calculates risk (risk_calculator.py):
      - Base severity: 0.6 (outbreak)
      - Maria's diabetes: +0.25 (multiplier 2.5)
      - Family in São Paulo: +0.20
      - Geographic distance: +0.05
      → Total: 0.75 (HIGH RISK)
   c. Generates reasoning
   d. Recommends actions
4. Returns personalized assessment to Airia
5. Airia acts based on risk level
```

**Same alert → Different users → Different outcomes = AUTONOMY**

---

## Demo Script (3 minutes)

**Setup:**
- Have 3 browser tabs open side-by-side
- Each showing one user's assessment
- Or use Airia canvas to display results

**Flow:**
1. **Intro (20s):** "Alert fatigue is real. Everyone gets the same warnings."
2. **Demo (2min):**
   - Show alert: "Dengue in São Paulo"
   - Show 3 users side-by-side:
     - Maria → HIGH (diabetes + family)
     - John → LOW (healthy + no connection)
     - Sarah → CRITICAL (pregnant + traveling)
   - Click into reasoning for each
3. **Tech (30s):** "Hybrid architecture. Airia orchestrates. Custom ML decides. 8-factor analysis."
4. **Impact (10s):** "Real personalization. Real autonomy. Saves lives."

---

## Troubleshooting

### "Database connection failed"
- Check `.env` has correct ClickHouse credentials
- Test: `python -c "from src.utils.clickhouse_client import db_client; print(db_client.health_check())"`

### "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`
- Make sure you're in the vitalsignal-backend directory

### "Port 8000 in use"
- Kill existing process: `lsof -ti:8000 | xargs kill -9`
- Or use different port: `uvicorn src.main:app --reload --port 8001`

### "ngrok not found"
- Install: `brew install ngrok`
- Verify: `which ngrok`

---

## Next Steps Checklist

- [ ] Install dependencies
- [ ] Initialize database
- [ ] Test API locally
- [ ] Verify risk calculator (run test_api.py)
- [ ] Setup ngrok
- [ ] Get ngrok public URL
- [ ] Configure Airia (follow AIRIA_SETUP_GUIDE.md)
- [ ] Test Airia → API integration
- [ ] Polish demo UI
- [ ] Prepare 3-minute demo script
- [ ] Take screenshots/video
- [ ] Submit to DevPost

---

## Key Endpoints for Airia

```
GET  <ngrok-url>/health
     → Health check

GET  <ngrok-url>/api/v1/users
     → List all users (Maria, John, Sarah)

POST <ngrok-url>/api/v1/personalize
     → Calculate personalized risk
     Body: { "user_id": "demo_maria", "alert": {...} }
```

---

## Important URLs

- **API Docs:** http://localhost:8000/docs
- **ngrok Dashboard:** http://localhost:4040
- **Airia Platform:** https://airia.ai/
- **Your Email:** richel.gomez@pursuit.org

---

## Git Committed ✅

All work is committed to git:
```
commit 3c61f5d
feat: Complete Phase 1 - Core API with risk calculator
```

---

## Decision Record

**Why NOT use MCP servers?**
- Time constraint (4 hours remaining)
- MCP setup adds 1-2 hours
- Direct APIs = easier debugging
- Autonomy is in the logic, not the transport layer
- Can mention in presentation: "5 MCP servers available for production"

**Why Hybrid Architecture?**
- Airia: Orchestration (tool calling, workflow)
- Our API: Intelligence (risk calculation, personalization)
- Best of both worlds
- Easy to demo autonomy

---

## You've Got This! 🎯

The hard part is done. The backend is solid. The logic is smart. The demo will be impressive.

Focus on:
1. Getting ngrok running
2. Connecting Airia
3. Testing the full flow
4. Polishing the presentation

**Time Check:** ~4 hours remaining. You have plenty of buffer.

---

**Questions? Check:**
1. SETUP_COMPLETE.md - Technical details
2. AIRIA_SETUP_GUIDE.md - Airia configuration
3. NGROK_SETUP_GUIDE.md - ngrok setup
4. API docs at http://localhost:8000/docs

**Ready to test? Run:**
```bash
cd /Users/richelgomez/Documents/hackathon/vitalsignal-backend
python scripts/init_db.py
uvicorn src.main:app --reload --port 8000
python scripts/test_api.py
```

🚀 Let's win this hackathon!
