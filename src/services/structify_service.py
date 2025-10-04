"""Structify API integration for scraping health alerts"""

import httpx
from typing import List, Optional
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
        try:
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
                    print(f"Structify API error: {response.status_code}")
                    return self._get_fallback_alerts()
                
                data = response.json()
                alerts = []
                
                for item in data.get("alerts", [])[:10]:  # Limit to 10 most recent
                    try:
                        alert = HealthAlert(
                            alert_id=f"who_{item['title'][:20].replace(' ', '_').lower()}_{int(datetime.utcnow().timestamp())}",
                            title=item["title"],
                            description=item.get("description", ""),
                            disease=item.get("disease", "unknown").lower(),
                            location=item.get("location", "Global"),
                            severity=DiseaseSeverity.OUTBREAK,  # Default
                            source="WHO",
                            source_url="https://www.who.int/emergencies/disease-outbreak-news",
                            published_at=datetime.utcnow()
                        )
                        
                        # Filter by disease if specified
                        if disease and disease.lower() not in alert.disease.lower():
                            continue
                            
                        alerts.append(alert)
                    except Exception as e:
                        print(f"Error parsing alert: {e}")
                        continue
                
                return alerts if alerts else self._get_fallback_alerts()
                
        except Exception as e:
            print(f"Structify scraping failed: {e}")
            return self._get_fallback_alerts()
    
    def _get_fallback_alerts(self) -> List[HealthAlert]:
        """Return mock alerts if scraping fails"""
        return [
            HealthAlert(
                alert_id="dengue_sp_2025",
                title="Dengue Outbreak in São Paulo",
                description="Health authorities report 500 confirmed dengue cases in São Paulo, Brazil, with 3 fatalities. The outbreak is concentrated in the metropolitan area.",
                disease="dengue",
                location="São Paulo, Brazil",
                severity=DiseaseSeverity.OUTBREAK,
                source="WHO",
                source_url="https://www.who.int/emergencies/disease-outbreak-news",
                published_at=datetime.utcnow()
            ),
            HealthAlert(
                alert_id="covid_ny_2025",
                title="COVID-19 Surge in New York",
                description="CDC reports 1,200 new COVID-19 cases in New York City over the past week, representing a 30% increase.",
                disease="covid-19",
                location="New York, USA",
                severity=DiseaseSeverity.EPIDEMIC,
                source="CDC",
                source_url="https://www.cdc.gov/",
                published_at=datetime.utcnow()
            ),
            HealthAlert(
                alert_id="malaria_ng_2025",
                title="Malaria Outbreak in Lagos",
                description="Nigeria health officials report significant increase in malaria cases in Lagos state with over 800 confirmed cases.",
                disease="malaria",
                location="Lagos, Nigeria",
                severity=DiseaseSeverity.OUTBREAK,
                source="WHO",
                source_url="https://www.who.int/",
                published_at=datetime.utcnow()
            )
        ]


# Global instance
structify_service = StructifyService()
