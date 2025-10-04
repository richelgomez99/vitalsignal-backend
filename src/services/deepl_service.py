"""DeepL API integration for translation"""

import httpx
from typing import Optional
from src.config import settings


class DeepLService:
    """Service for translating health alerts using DeepL"""
    
    def __init__(self):
        self.api_key = settings.deepl_api_key
        self.base_url = "https://api-free.deepl.com/v2"  # Free tier URL
        
    async def translate_text(
        self, 
        text: str, 
        target_language: str,
        source_language: Optional[str] = None
    ) -> dict:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., "ES", "FR", "PT", "ZH")
            source_language: Optional source language (auto-detect if not provided)
            
        Returns:
            Dictionary with translated text and detected source language
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "text": [text],
                    "target_lang": target_language.upper()
                }
                
                if source_language:
                    payload["source_lang"] = source_language.upper()
                
                response = await client.post(
                    f"{self.base_url}/translate",
                    headers={
                        "Authorization": f"DeepL-Auth-Key {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    translation = data["translations"][0]
                    return {
                        "translated_text": translation["text"],
                        "detected_source_language": translation.get("detected_source_language", "EN"),
                        "target_language": target_language.upper()
                    }
                else:
                    print(f"DeepL API error: {response.status_code}")
                    return self._get_fallback_translation(text, target_language)
                    
        except Exception as e:
            print(f"DeepL translation error: {e}")
            return self._get_fallback_translation(text, target_language)
    
    def _get_fallback_translation(self, text: str, target_language: str) -> dict:
        """Return fallback when translation fails"""
        return {
            "translated_text": f"[{target_language}] {text}",
            "detected_source_language": "EN",
            "target_language": target_language.upper(),
            "note": "Translation service unavailable - showing original text with language tag"
        }


# Global instance
deepl_service = DeepLService()
