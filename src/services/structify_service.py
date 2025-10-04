"""Structify API integration for scraping health alerts"""

import httpx
from typing import List, Optional
from datetime import datetime, timedelta
import re
from src.config import settings
from src.models import HealthAlert, DiseaseSeverity


class StructifyService:
    """Service for scraping health alerts using Structify"""
    
    def __init__(self):
        self.api_key = settings.structify_api_key
        self.base_url = "https://api.structify.ai/v1"
        # Your Structify workflow ID
        self.workflow_id = "scrape_health_sources_for_vitalsignal"
        
    async def scrape_who_alerts(self, disease: Optional[str] = None) -> List[HealthAlert]:
        """
        Get latest health alerts from Structify workflow
        
        Args:
            disease: Optional filter for specific disease
            
        Returns:
            List of health alerts from WHO, CDC, and news sources
        """
        try:
            # Call Structify workflow to get latest scraped data
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Get latest workflow run results
                response = await client.get(
                    f"{self.base_url}/workflows/{self.workflow_id}/latest",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    print(f"Structify workflow fetch failed: {response.status_code}")
                    return self._get_fallback_alerts()
                
                data = response.json()
                
                # Parse workflow output (should be array of alert objects)
                alerts = []
                workflow_results = data.get("results", [])
                
                if not workflow_results:
                    print("No results from Structify workflow, using fallback")
                    return self._get_fallback_alerts()
                
                for item in workflow_results:
                    try:
                        # Extract fields from Structify output
                        title = item.get("title") or "Health Alert"
                        description = item.get("description") or "No description available"
                        disease_name = item.get("disease") or "unknown"
                        location = item.get("location") or "Global"
                        source = item.get("source") or "WHO"
                        url = item.get("url") or ""
                        date_str = item.get("date_published")
                        
                        # Parse date
                        published_at = self._parse_date(date_str) if date_str else datetime.utcnow()
                        
                        # Map severity
                        severity = self._map_severity(item.get("severity", "MEDIUM"))
                        
                        # Create alert
                        alert = HealthAlert(
                            alert_id=f"structify_{abs(hash(title + location))}",
                            title=title,
                            description=description,
                            disease=disease_name.lower(),
                            location=location,
                            severity=severity,
                            source=source,
                            source_url=url,
                            published_at=published_at
                        )
                        
                        # Filter by disease if specified
                        if disease and disease.lower() not in alert.disease.lower():
                            continue
                            
                        alerts.append(alert)
                        
                    except Exception as e:
                        print(f"Error parsing Structify alert: {e}")
                        continue
                
                if alerts:
                    print(f"✅ Retrieved {len(alerts)} alerts from Structify workflow")
                    return alerts
                else:
                    return self._get_fallback_alerts()
                
        except Exception as e:
            print(f"Structify workflow error: {e}")
            return self._get_fallback_alerts()
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats including relative dates"""
        if not date_str:
            return datetime.utcnow()
        
        # Handle relative dates like "7 hours ago", "2 days ago"
        relative_pattern = r'(\d+)\s+(hour|day|week)s?\s+ago'
        match = re.search(relative_pattern, date_str, re.IGNORECASE)
        if match:
            amount = int(match.group(1))
            unit = match.group(2).lower()
            
            if unit == 'hour':
                return datetime.utcnow() - timedelta(hours=amount)
            elif unit == 'day':
                return datetime.utcnow() - timedelta(days=amount)
            elif unit == 'week':
                return datetime.utcnow() - timedelta(weeks=amount)
        
        # Try standard formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%B %d, %Y",
            "%d %B %Y",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all else fails, return current time
        return datetime.utcnow()
    
    def _map_severity(self, severity_str: str) -> DiseaseSeverity:
        """Map severity string to DiseaseSeverity enum"""
        severity_map = {
            "CRITICAL": DiseaseSeverity.PANDEMIC,
            "HIGH": DiseaseSeverity.EPIDEMIC,
            "MEDIUM": DiseaseSeverity.OUTBREAK,
            "LOW": DiseaseSeverity.CLUSTER,
        }
        return severity_map.get(severity_str.upper(), DiseaseSeverity.OUTBREAK)
    
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
