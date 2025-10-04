"""PhenoML API integration for medical code enrichment"""

import httpx
from typing import Optional, Dict, Any
from src.config import settings


class PhenoMLService:
    """Service for enriching health alerts with FHIR/SNOMED/ICD-10 codes"""
    
    def __init__(self):
        self.base_url = settings.phenoml_base_url
        self.api_token = settings.phenoml_api_token
    
    async def explain_medical_codes(self, disease_name: str, icd10_code: str, snomed_code: str) -> Dict[str, Any]:
        """
        Convert medical codes to patient-friendly explanations
        
        Args:
            disease_name: Name of the disease
            icd10_code: ICD-10 code
            snomed_code: SNOMED code
            
        Returns:
            Plain language explanation with symptoms, treatment, prevention
        """
        # Generate patient-friendly explanation
        explanation = {
            "disease": disease_name,
            "what_it_is": self._get_disease_explanation(disease_name),
            "common_symptoms": self._get_symptoms(disease_name),
            "how_it_spreads": self._get_transmission(disease_name),
            "prevention_tips": self._get_prevention(disease_name),
            "when_to_seek_care": self._get_care_recommendations(disease_name),
            "medical_codes": {
                "icd10": icd10_code,
                "snomed": snomed_code
            }
        }
        return explanation
    
    def _get_disease_explanation(self, disease: str) -> str:
        """Plain language disease explanation"""
        explanations = {
            "dengue": "Dengue is a viral infection spread by mosquitoes. It causes flu-like symptoms and can be serious.",
            "malaria": "Malaria is a life-threatening disease spread by infected mosquitoes. It causes fever and flu-like illness.",
            "marburg": "Marburg virus disease is a rare but severe hemorrhagic fever that affects humans and other primates.",
            "mpox": "Mpox (monkeypox) is a viral disease that causes a rash and flu-like symptoms.",
            "avian influenza": "Avian influenza (bird flu) is a virus that primarily affects birds but can occasionally infect humans."
        }
        return explanations.get(disease.lower(), f"{disease} is an infectious disease requiring medical attention.")
    
    def _get_symptoms(self, disease: str) -> list:
        """Common symptoms list"""
        symptoms_map = {
            "dengue": ["High fever", "Severe headache", "Pain behind eyes", "Joint and muscle pain", "Rash", "Mild bleeding"],
            "malaria": ["Fever and chills", "Headache", "Nausea and vomiting", "Muscle pain", "Fatigue"],
            "marburg": ["High fever", "Severe headache", "Muscle aches", "Bleeding or bruising", "Confusion"],
            "mpox": ["Rash", "Fever", "Swollen lymph nodes", "Headache", "Muscle aches"],
            "avian influenza": ["Fever", "Cough", "Sore throat", "Muscle aches", "Difficulty breathing"]
        }
        return symptoms_map.get(disease.lower(), ["Fever", "Fatigue", "Consult a doctor for specific symptoms"])
    
    def _get_transmission(self, disease: str) -> str:
        """How disease spreads"""
        transmission_map = {
            "dengue": "Spread by mosquito bites, particularly Aedes mosquitoes. Cannot spread person-to-person.",
            "malaria": "Transmitted through bites of infected Anopheles mosquitoes.",
            "marburg": "Spreads through contact with infected bodily fluids or contaminated materials.",
            "mpox": "Spreads through close contact with infected person, animals, or contaminated materials.",
            "avian influenza": "Mainly spreads from infected birds. Human-to-human transmission is rare."
        }
        return transmission_map.get(disease.lower(), "Consult health authorities for transmission information.")
    
    def _get_prevention(self, disease: str) -> list:
        """Prevention tips"""
        prevention_map = {
            "dengue": ["Use mosquito repellent", "Wear long sleeves and pants", "Use mosquito nets", "Eliminate standing water"],
            "malaria": ["Take antimalarial medication if traveling", "Use insecticide-treated bed nets", "Apply mosquito repellent"],
            "marburg": ["Avoid contact with infected persons", "Use protective equipment", "Practice good hygiene"],
            "mpox": ["Avoid contact with infected people or animals", "Practice good hand hygiene", "Avoid sharing personal items"],
            "avian influenza": ["Avoid contact with sick or dead birds", "Cook poultry thoroughly", "Practice good hand hygiene"]
        }
        return prevention_map.get(disease.lower(), ["Follow local health authority guidelines", "Practice good hygiene"])
    
    def _get_care_recommendations(self, disease: str) -> str:
        """When to seek medical care"""
        return "Seek immediate medical attention if you experience severe symptoms or if symptoms worsen. Early treatment is important."
    
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
            # Check if token is available
            if not self.api_token:
                print("PhenoML token not configured, using fallback")
                return self._get_fallback_codes(disease_name)
            
            # Create text for analysis
            text = f"{disease_name}. {description}" if description else disease_name
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/lang2fhir/create",
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "R4",
                        "resource": "auto",
                        "text": text
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    fhir_data = response.json()
                    print(f"✅ PhenoML enrichment successful for {disease_name}")
                    return self._parse_fhir_response(fhir_data, disease_name)
                else:
                    print(f"PhenoML API error: {response.status_code} - {response.text}")
                    return self._get_fallback_codes(disease_name)
                    
        except Exception as e:
            print(f"PhenoML enrichment error: {e}")
            return self._get_fallback_codes(disease_name)
    
    def _parse_fhir_response(self, fhir_data: Dict[str, Any], disease_name: str) -> Dict[str, Any]:
        """Parse FHIR response to extract medical codes"""
        result = {
            "snomed_code": None,
            "snomed_display": None,
            "icd10_code": None,
            "icd10_display": None,
            "fhir_data": fhir_data
        }
        
        try:
            # PhenoML response structure
            if "code" in fhir_data and "coding" in fhir_data["code"]:
                coding_list = fhir_data["code"]["coding"]
            elif "Condition" in fhir_data:
                condition = fhir_data.get("Condition", {})
                code = condition.get("code", {})
                coding_list = code.get("coding", [])
            else:
                # Try direct access
                coding_list = fhir_data.get("coding", [])
            
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
            print(f"Error parsing FHIR for {disease_name}: {e}")
            # Fall back to coded response
            return self._get_fallback_codes(disease_name)
        
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
