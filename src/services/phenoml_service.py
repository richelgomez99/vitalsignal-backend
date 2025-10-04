"""PhenoML API integration for medical code enrichment"""

import httpx
from typing import Optional, Dict, Any
from src.config import settings


class PhenoMLService:
    """Service for enriching health alerts with FHIR/SNOMED/ICD-10 codes"""
    
    def __init__(self):
        self.base_url = settings.phenoml_base_url
        self.email = settings.phenoml_email
        self.password = settings.phenoml_password
        self._token: Optional[str] = None
        
    async def _get_auth_token(self) -> str:
        """Get authentication token from PhenoML"""
        if self._token:
            return self._token
            
        try:
            async with httpx.AsyncClient() as client:
                # PhenoML uses Basic Auth to get Bearer token
                auth = (self.email, self.password)
                response = await client.post(
                    f"{self.base_url}/auth/token",
                    auth=auth,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._token = data.get("access_token")
                    return self._token
                else:
                    print(f"PhenoML auth failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"PhenoML auth error: {e}")
            return None
    
    async def enrich_disease(self, disease_name: str, description: str = "") -> Dict[str, Any]:
        """
        Enrich disease information with medical codes
        
        Args:
            disease_name: Name of the disease
            description: Optional description for context
            
        Returns:
            Dictionary with SNOMED, ICD-10 codes and FHIR data
        """
        try:
            # Get auth token
            token = await self._get_auth_token()
            if not token:
                return self._get_fallback_codes(disease_name)
            
            # Create text for analysis
            text = f"{disease_name}. {description}" if description else disease_name
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/lang2fhir/create",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "resource_type": "condition-encounter-diagnosis",
                        "version": "R4"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    fhir_data = response.json()
                    return self._parse_fhir_response(fhir_data)
                else:
                    print(f"PhenoML API error: {response.status_code}")
                    return self._get_fallback_codes(disease_name)
                    
        except Exception as e:
            print(f"PhenoML enrichment error: {e}")
            return self._get_fallback_codes(disease_name)
    
    def _parse_fhir_response(self, fhir_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse FHIR response to extract medical codes"""
        result = {
            "snomed_code": None,
            "snomed_display": None,
            "icd10_code": None,
            "icd10_display": None,
            "fhir_data": fhir_data
        }
        
        try:
            # Navigate FHIR structure: Condition → code → coding
            condition = fhir_data.get("Condition", {})
            code = condition.get("code", {})
            coding_list = code.get("coding", [])
            
            # Extract SNOMED and ICD-10 codes
            for coding in coding_list:
                system = coding.get("system", "")
                
                if "snomed" in system.lower():
                    result["snomed_code"] = coding.get("code")
                    result["snomed_display"] = coding.get("display")
                    
                elif "icd" in system.lower():
                    result["icd10_code"] = coding.get("code")
                    result["icd10_display"] = coding.get("display")
            
        except Exception as e:
            print(f"Error parsing FHIR: {e}")
        
        return result
    
    def _get_fallback_codes(self, disease_name: str) -> Dict[str, Any]:
        """Return fallback medical codes for common diseases"""
        
        # Common disease code mappings
        fallback_map = {
            "dengue": {
                "snomed_code": "38362002",
                "snomed_display": "Dengue fever",
                "icd10_code": "A90",
                "icd10_display": "Dengue fever [classical dengue]"
            },
            "covid-19": {
                "snomed_code": "840539006",
                "snomed_display": "COVID-19",
                "icd10_code": "U07.1",
                "icd10_display": "COVID-19"
            },
            "malaria": {
                "snomed_code": "61462000",
                "snomed_display": "Malaria",
                "icd10_code": "B54",
                "icd10_display": "Unspecified malaria"
            },
            "ebola": {
                "snomed_code": "37109004",
                "snomed_display": "Ebola virus disease",
                "icd10_code": "A98.4",
                "icd10_display": "Ebola virus disease"
            },
            "chikungunya": {
                "snomed_code": "302835009",
                "snomed_display": "Chikungunya",
                "icd10_code": "A92.0",
                "icd10_display": "Chikungunya virus disease"
            }
        }
        
        disease_key = disease_name.lower().replace(" ", "-")
        return fallback_map.get(disease_key, {
            "snomed_code": None,
            "snomed_display": f"{disease_name} (code not available)",
            "icd10_code": None,
            "icd10_display": None,
            "fhir_data": None
        })


# Global instance
phenoml_service = PhenoMLService()
