# VitalSignal Project Plan

**Project:** Personal Health Guardian AI Agent
**Hackathon:** Airia AI Agents Competition
**Status:** Phase 2 - Tool Integration (4 of 7 tools completed)
**Time Remaining:** ~3.5 hours until 4:30 PM deadline
**Demo:** 3-minute live presentation

---

## Timeline Breakdown
### Phase 1: Core API Development (90 min) - **CRITICAL PATH**
**Goal:** Working FastAPI server with personalization logic

- ✅ Project structure setup (15 min)
- [ ] ClickHouse schema design + creation (20 min)
- [ ] Pydantic models (15 min)
- [ ] Risk calculator core logic (30 min)
- [ ] Main API endpoints (10 min)

### Phase 2: External Integrations (75 min)
**Goal:** Connect to all 6 external tools

- [ ] Structify client (alert scraping) (15 min)
- [ ] PhenoML integration (medical enrichment) (15 min)
- [ ] DeepL client (translation) (10 min)
- [ ] Freepik client (image generation) (15 min)
- [ ] SendGrid client (email notifications) (10 min)
- [ ] ClickHouse client (database) (10 min)

### Phase 3: Intelligence Layer (60 min)
**Goal:** Demonstrate non-deterministic, adaptive behavior

- [ ] Multi-factor risk scoring algorithm (20 min)
- [ ] User profile matching logic (15 min)
- [ ] Learning engine (feedback → behavior adaptation) (15 min)
- [ ] Medical knowledge base (disease-condition interactions) (10 min)

### Phase 4: Demo Preparation (60 min)
**Goal:** Working demo with 3 users showing different outcomes

- [ ] Seed database with 3 demo users (10 min)
- [ ] Create demo HTML dashboard (20 min)
- [ ] Test end-to-end flow (15 min)
- [ ] Prepare presentation talking points (15 min)

### Phase 5: Deployment + Buffer (45 min)
**Goal:** Accessible URL for demo

- [ ] Test all integrations (15 min)
- [ ] Deploy via ngrok OR Railway (20 min)
- [ ] Final walkthrough (10 min)

---

## Critical Path Items

1. **ClickHouse schema** - Blocks user creation
2. **Risk calculator** - Core autonomy demonstration
3. **3 demo users** - Show personalization
4. **Working API** - Everything depends on this

---

## Dependencies

```
ClickHouse Schema
    ↓
User Creation
    ↓
Risk Calculator ← Medical Knowledge
    ↓
External Integrations (parallel)
    ↓
End-to-End Testing
    ↓
Demo Dashboard
```

---

## Risk Mitigation

### If We Run Out of Time:

**MVP Scope (minimum viable demo):**
1. Risk calculator with hard-coded users (no database)
2. Mock external API responses (JSON files)
3. Console output instead of SendGrid emails
4. Simple HTML page showing 3 different risk scores

**What NOT to cut:**
- Risk scoring logic (autonomy judging)
- 3 different user outcomes (personalization proof)
- At least 3 real external tool integrations (tool use judging)

**What CAN be mocked:**
- Learning engine (show architecture, don't implement)
- DeepL translation (use simple dict)
- Freepik images (use placeholder URLs)

---

## Success Metrics

**Must Have (for submission):**
- [ ] API running at public URL
- [ ] 3 demo users with different profiles
- [ ] Same alert → 3 different risk scores
- [ ] At least 3 external tools actually called
- [ ] 3-minute demo script ready

**Nice to Have:**
- [ ] Learning engine implemented
- [ ] Email notifications working
- [ ] Beautiful demo UI
- [ ] All 6 tools integrated

---

## Presentation Strategy

**Structure (3 minutes):**
1. **Problem** (20 sec) - Alert fatigue, one-size-fits-all warnings
2. **Demo** (2 min) - Show same alert → 3 outcomes live
3. **Tech** (30 sec) - Hybrid architecture, autonomy explanation
4. **Impact** (10 sec) - Real-world health personalization

**Key Message:**
"VitalSignal doesn't just forward alerts - it THINKS about what matters to YOU."

---

## Next Actions (Immediate)

1. Create ClickHouse schema
2. Implement Pydantic models
3. Build risk calculator
4. Test with hard-coded data

**Time Check:** Update this plan after Phase 1 completion
