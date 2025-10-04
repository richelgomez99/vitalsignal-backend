# VitalSignal Quick Reference

**Last Updated:** 2025-10-04 11:55 AM
**Status:** ✅ Backend Running, Ready for Airia Integration

---

## Your Active URLs

```
ngrok Public URL: https://chelsey-ideographical-emelia.ngrok-free.dev
Local API:        http://localhost:8000
API Docs:         http://localhost:8000/docs
ngrok Dashboard:  http://localhost:4040
```

---

## Airia Tool URLs

**Tool #1: Get VitalSignal Users**
```
Method: GET
URL: https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users
Headers: Content-Type: application/json, Accept: application/json
Auth: None
```

**Tool #2: Personalize Risk Assessment**
```
Method: POST
URL: https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize
Headers: Content-Type: application/json, Accept: application/json
Auth: None
Body: Use <variable/> syntax (see AIRIA_OFFICIAL_TOOL_GUIDE.md)
```

---

## Test Commands

```bash
# Health check
curl https://chelsey-ideographical-emelia.ngrok-free.dev/health

# Get users
curl https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users

# Test personalization (Maria - should be HIGH risk)
curl -X POST https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_maria",
    "alert": {
      "alert_id": "dengue_sp_001",
      "title": "Dengue Outbreak in São Paulo",
      "description": "500 confirmed cases",
      "disease": "dengue",
      "location": "São Paulo, Brazil",
      "severity": "outbreak",
      "published_at": "2025-10-04T15:00:00Z"
    }
  }'
```

---

## Terminal Layout

**Terminal 1:** FastAPI Server
```bash
cd /Users/richelgomez/Documents/hackathon/vitalsignal-backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**Terminal 2:** ngrok Tunnel
```bash
ngrok http 8000
```

**Terminal 3:** Testing/Commands
```bash
# Use for curl tests, git commits, etc.
```

---

## Demo Users

| User | Profile | Expected Risk |
|------|---------|---------------|
| **Maria Silva** | Diabetic, Sister in São Paulo | HIGH (0.70-0.80) |
| **John Smith** | Healthy, No connections | LOW (0.15-0.25) |
| **Sarah Johnson** | Pregnant, Traveling to Brazil | CRITICAL (0.85-0.95) |

**User IDs:**
- `demo_maria`
- `demo_john`
- `demo_sarah`

---

## Airia Agent Prompt

```
You are VitalSignal, a personal health alert personalization AI agent.

WORKFLOW:
1. When you receive a health alert, FIRST use the "Get VitalSignal Users" tool
2. For EACH user returned, use the "Personalize Risk Assessment" tool with:
   - user_id from the Get Users tool output
   - alert information from the input

3. Present results as a comparison showing ALL users:
   - User name and key profile details
   - Risk Level (CRITICAL/HIGH/MEDIUM/LOW) - highlight prominently
   - Risk Score (0-1 numeric)
   - Top 3 reasoning points
   - Recommended actions

IMPORTANT: Show ALL three users to demonstrate personalization.
Different users WILL get different risk levels for the same alert.

FORMAT OUTPUT as a clear comparison table or side-by-side view.
```

---

## Test Alert for Demo

```
Title: Dengue Outbreak in São Paulo
Description: Health authorities report 500 confirmed dengue fever cases in São Paulo, Brazil, with 3 fatalities. The outbreak is concentrated in the metropolitan area.
Disease: dengue
Location: São Paulo, Brazil
Severity: outbreak
Date: 2025-10-04T15:00:00Z
```

---

## API Credentials

**Environment:** development
**ClickHouse:** c68xuydw5q.us-east1.gcp.clickhouse.cloud
**Python:** 3.12.8 (venv active)
**ngrok Account:** richelgomez99 (Free Plan)

---

## Next Steps Checklist

- [x] Backend running
- [x] ngrok tunnel active
- [x] Database initialized
- [ ] Create Airia Tool #1 (Get Users)
- [ ] Create Airia Tool #2 (Personalize)
- [ ] Add tools to AI Model in Agent
- [ ] Configure Agent prompt
- [ ] Test full workflow
- [ ] Prepare demo presentation
- [ ] Submit to DevPost

---

## Time Remaining

**Current:** 11:55 AM
**Deadline:** 4:30 PM
**Remaining:** ~4 hours 35 minutes

**Critical Path:**
1. Create Airia tools (15 min)
2. Test integration (10 min)
3. Demo preparation (30 min)
4. Buffer for debugging (3+ hours)

---

## Key Files

- **START_HERE.md** - Main entry point
- **AIRIA_OFFICIAL_TOOL_GUIDE.md** - Step-by-step Airia setup
- **QUICK_REFERENCE.md** - This file
- **tasks.md** - Task checklist
- **plan.md** - Project timeline

---

## Support Links

- **Airia Platform:** https://airia.ai/
- **Airia Docs:** https://explore.airia.com/
- **ngrok Dashboard:** https://dashboard.ngrok.com/
- **FastAPI Docs:** http://localhost:8000/docs

---

**Everything is ready. Time to create those Airia tools!** 🚀
