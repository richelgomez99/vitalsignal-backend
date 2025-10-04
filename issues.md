# VitalSignal Issues Tracker

**Last Updated:** 2025-10-04 11:27 AM

---

## Active Issues 🔴

*(No active issues yet)*

---

## Resolved Issues ✅

*(Resolved issues will appear here)*

---

## Questions/Decisions Needed 🤔

### Decision Log

**Decision 1: MCP vs Direct APIs**
- **Question:** Use MCP servers or direct API calls for external tools?
- **Decision:** Direct APIs
- **Rationale:** 
  - Time constraint (4.5 hours)
  - Already have API documentation
  - Easier debugging during demo
  - Autonomy judging based on logic, not transport layer
- **Status:** Resolved
- **Date:** 2025-10-04

**Decision 2: Deployment Strategy**
- **Question:** Local + ngrok vs cloud deployment?
- **Decision:** Start with local + ngrok, structure for easy cloud migration
- **Rationale:**
  - Faster iteration during development
  - Can switch to cloud if needed
  - Docker + env vars make migration simple
- **Status:** Resolved
- **Date:** 2025-10-04

---

## Known Limitations

### MVP Scope
- Learning engine may be simplified (rule-based vs ML)
- Some external APIs may be mocked if rate limits hit
- UI will be minimal but functional

### Technical Debt
- Error handling can be improved post-hackathon
- Testing coverage minimal (focus on core logic)
- No authentication layer (demo purposes)

---

## Future Enhancements (Post-Hackathon)

- [ ] Add user authentication
- [ ] Implement proper ML model for learning
- [ ] Add more medical conditions to knowledge base
- [ ] Real-time WebSocket alerts
- [ ] Mobile app
- [ ] Integration with actual health data sources (Fitbit, Apple Health)
- [ ] Multi-language support beyond DeepL
- [ ] Advanced FHIR resource parsing

---

## Bug Template

```markdown
## Issue: [Short Description]

**Severity:** Critical / High / Medium / Low
**Status:** Open / In Progress / Resolved

**Description:**
What's broken?

**Steps to Reproduce:**
1. Step 1
2. Step 2

**Expected Behavior:**
What should happen?

**Actual Behavior:**
What actually happens?

**Potential Cause:**
Initial diagnosis

**Solution:**
How we fixed it

**Resolved:** YYYY-MM-DD
```

---

## Notes

- Keep this updated throughout development
- Log ALL blockers immediately
- Document decisions for presentation Q&A
