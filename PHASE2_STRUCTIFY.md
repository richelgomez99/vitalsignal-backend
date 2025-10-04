# Phase 2: Structify Integration (1 hour)

**Goal:** Add real-time WHO/CDC alert scraping via Structify

---

## Step 1: Create Structify Service (15 min)

**File:** `src/services/structify_service.py`

```python
"""Structify API integration for scraping health alerts"""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.config import settings
from src.models import HealthAlert, DiseaseSeverity

class StructifyService:
    """Service for scraping health alerts using Structify"""
    
    def __init__(self):
        self.api_key = settings.structify_api_key
        self.base_url = "https://api.structify.ai/v1"
        
    async def scrape_who_alerts(self, disease: Optional[str] = None) -> List[HealthAlert]:
        """
        Scrape latest alerts from WHO
        
        Args:
            disease: Optional filter for specific disease
            
        Returns:
            List of health alerts
        """
        async with httpx.AsyncClient() as client:
            # Structify call to scrape WHO disease outbreak news
            response = await client.post(
                f"{self.base_url}/extract",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": "https://www.who.int/emergencies/disease-outbreak-news",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "alerts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "disease": {"type": "string"},
                                        "location": {"type": "string"},
                                        "description": {"type": "string"},
                                        "date": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            alerts = []
            
            for item in data.get("alerts", [])[:10]:  # Limit to 10 most recent
                try:
                    alert = HealthAlert(
                        alert_id=f"who_{item['title'][:20].replace(' ', '_').lower()}",
                        title=item["title"],
                        description=item.get("description", ""),
                        disease=item.get("disease", "unknown"),
                        location=item.get("location", "Global"),
                        severity=DiseaseSeverity.OUTBREAK,  # Default
                        source="WHO",
                        source_url="https://www.who.int/emergencies/disease-outbreak-news",
                        published_at=datetime.fromisoformat(item["date"]) if item.get("date") else datetime.utcnow()
                    )
                    
                    if disease and disease.lower() not in alert.disease.lower():
                        continue
                        
                    alerts.append(alert)
                except Exception as e:
                    print(f"Error parsing alert: {e}")
                    continue
            
            return alerts

structify_service = StructifyService()
```

---

## Step 2: Add API Endpoint (10 min)

**Add to `src/main.py`:**

```python
from src.services.structify_service import structify_service

@app.get("/api/v1/alerts/scrape", response_model=List[HealthAlert], tags=["Alerts"])
async def scrape_latest_alerts(
    disease: Optional[str] = None,
    limit: int = 10
):
    """
    Scrape latest health alerts from WHO using Structify
    
    Args:
        disease: Optional filter for specific disease (e.g., "dengue", "covid")
        limit: Maximum number of alerts to return (default 10)
        
    Returns:
        List of health alerts scraped from WHO
        
    ## Example:
    - GET /api/v1/alerts/scrape
    - GET /api/v1/alerts/scrape?disease=dengue
    """
    try:
        alerts = await structify_service.scrape_who_alerts(disease=disease)
        return alerts[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )
```

---

## Step 3: Create Airia Tool #3 (15 min)

**In Airia:**

1. Tools → Create New Tool → Custom API Tool

2. **Tool Name:** `Scrape WHO Alerts`

3. **Tool Description:**
```
Scrape live health alerts from the World Health Organization (WHO) website.

Use this tool to get REAL-TIME disease outbreak information instead of using hardcoded alerts.

Optional parameter:
- disease: Filter for specific disease (e.g., "dengue", "covid", "malaria")

Returns: Array of current health alerts with title, disease, location, description, severity, and date.

Use Case: Call this first to get real alerts, then call "Personalize Risk Assessment" for each user with each alert.
```

4. **API:** GET

5. **URL:** `https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/alerts/scrape`

6. **Headers:**
   - Content-Type: application/json
   - Accept: application/json

7. **Query Parameters:**
   Click "+ Add Parameter":
   - **Key:** disease
   - **Type:** String
   - **Required:** No
   - **Description:** Optional disease filter

8. **Authorization:** None

9. **Create Tool**

---

## Step 4: Test (10 min)

### Test 1: Manually via curl
```bash
curl https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/alerts/scrape
```

### Test 2: In Airia Tool
- Click "Test"
- Leave disease empty
- Should return WHO alerts

### Test 3: Full Agent Workflow
```
Get the latest WHO alerts and assess risk for all users.
```

Expected:
1. Scrapes real WHO data
2. Gets Maria & John
3. Calculates personalized risk for each alert/user combo

---

## Step 5: Update Agent Prompt (10 min)

```
You are VitalSignal, an AI health alert analyzer with access to live WHO data.

WORKFLOW:

1. Call "Scrape WHO Alerts" to get current disease outbreaks
2. Call "Get VitalSignal Users" to get all users
3. For EACH alert AND EACH user, call "Personalize Risk Assessment"
4. Present results grouped by user, showing their risk for each alert

FORMAT:
**User: [Name]**
- Alert 1: [Disease] in [Location] → Risk: [LEVEL] ([score])
- Alert 2: [Disease] in [Location] → Risk: [LEVEL] ([score])

This shows how one user gets different risks for different diseases.
```

---

## Fallback Plan (if Structify fails)

**Mock alerts endpoint:**

```python
@app.get("/api/v1/alerts/mock", response_model=List[HealthAlert])
async def get_mock_alerts():
    """Get mock WHO alerts for demo"""
    return [
        HealthAlert(
            alert_id="dengue_sp_2025",
            title="Dengue Outbreak in São Paulo",
            description="500 confirmed cases",
            disease="dengue",
            location="São Paulo, Brazil",
            severity=DiseaseSeverity.OUTBREAK,
            source="WHO",
            published_at=datetime.utcnow()
        ),
        HealthAlert(
            alert_id="covid_ny_2025",
            title="COVID-19 Surge in New York",
            description="1200 new cases",
            disease="covid-19",
            location="New York, USA",
            severity=DiseaseSeverity.EPIDEMIC,
            source="CDC",
            published_at=datetime.utcnow()
        )
    ]
```

---

## Time Check

**After Phase 2:** 1:30 PM  
**Remaining:** 3 hours

**Next:** Phase 3 (PhenoML) or Polish & Present?
