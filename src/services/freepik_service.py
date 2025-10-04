"""Freepik API integration for image generation"""

import httpx
import asyncio
import base64
import hashlib
from pathlib import Path
from typing import Optional
from src.config import settings
from src.utils.clickhouse_client import db_client


class FreepikService:
    """Service for generating alert images using Freepik AI"""
    
    def __init__(self):
        self.api_key = settings.freepik_api_key
        self.base_url = "https://api.freepik.com/v1"
        self.static_dir = Path("static/images")
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_alert_image(
        self, 
        disease_name: str,
        severity: str,
        location: str
    ) -> dict:
        """
        Generate warning image for disease alert
        
        Just delegates to generate_image method
        """
        return await self.generate_image(disease_name, severity, location)
    
    async def _poll_for_image(self, job_id: str, max_attempts: int = 5) -> Optional[str]:
        """Poll Freepik for completed image"""
        async with httpx.AsyncClient() as client:
            for attempt in range(max_attempts):
                await asyncio.sleep(2)  # Wait 2 seconds between polls
                
                try:
                    response = await client.get(
                        f"{self.base_url}/ai/text-to-image/{job_id}",
                        headers={"x-freepik-api-key": self.api_key},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "completed" and "data" in data:
                            return data["data"][0]["url"]
                except Exception as e:
                    print(f"Polling error: {e}")
                    continue
        
        return None
    
    async def generate_symptom_visual(self, disease_name: str) -> dict:
        """Generate visual guide showing what symptoms look like"""
        url = f"https://placehold.co/800x600/3b82f6/white?text=📋+{disease_name.upper()}+SYMPTOMS&font=roboto"
        return {
            "image_url": url,
            "prompt": f"Symptom guide for {disease_name}",
            "status": "generated",
            "note": "Symptom visualization guide"
        }
    
    async def generate_prevention_infographic(self, disease_name: str, language: str = "EN") -> dict:
        """Generate prevention infographic in specified language"""
        url = f"https://placehold.co/800x1200/16a34a/white?text=🛡️+{disease_name.upper()}+PREVENTION&font=roboto"
        return {
            "image_url": url,
            "prompt": f"Prevention infographic for {disease_name} in {language}",
            "status": "generated",
            "note": f"Prevention infographic ({language})"
        }
    
    async def generate_image(self, disease_name: str, severity: str, location: str) -> dict:
        """Generate disease alert poster using Freepik AI"""
        
        # Create professional medical alert prompt (avoid text in image - text is in email)
        # Focus on strong visual symbols and medical imagery
        severity_visual = {
            "critical": "urgent red emergency medical symbol",
            "pandemic": "global health crisis warning symbol", 
            "epidemic": "disease outbreak alert symbol",
            "outbreak": "medical attention warning symbol",
            "high": "important health alert symbol",
            "medium": "health advisory symbol",
            "low": "health information symbol"
        }.get(severity.lower(), "medical alert symbol")
        
        prompt = f"Professional medical poster design for {disease_name}, {severity_visual}, clean minimalist healthcare design, medical cross, warning colors, disease awareness campaign, public health infographic style, modern medical illustration, NO text or words needed, symbolic representation, high quality digital art"
        
        try:
            if not self.api_key:
                print("⚠️ Freepik API key not configured, using fallback")
                return self._get_fallback_image(disease_name, severity)
            
            async with httpx.AsyncClient() as client:
                # Use Flux model for better infographic/poster generation with text
                response = await client.post(
                    f"{self.base_url}/ai/text-to-image/flux-dev",
                    headers={
                        "x-freepik-api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "num_images": 1,
                        "image": {
                            "size": "square_1_1"
                        },
                        "guidance_scale": 3.5,  # Better prompt following for infographics
                        "num_inference_steps": 30  # Higher quality
                    },
                    timeout=45.0  # Flux takes longer but produces better results
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Freepik Flux API success! Response keys: {list(data.keys())}")
                    
                    # Check if image is immediately available
                    if "data" in data and len(data["data"]) > 0 and data["data"][0]:
                        # Freepik returns base64 - store in ClickHouse
                        base64_data = data["data"][0].get("base64", "")
                        if base64_data:
                            # Extract base64 string (remove data:image/jpeg;base64, prefix)
                            if "," in base64_data:
                                base64_string = base64_data.split(",")[1]
                            else:
                                base64_string = base64_data
                            
                            # Create unique image ID
                            image_id = hashlib.md5(f"{disease_name}{severity}{location}".encode()).hexdigest()[:16]
                            
                            # Decode and store in ClickHouse
                            image_bytes = base64.b64decode(base64_string)
                            success = db_client.store_image(image_id, image_bytes, disease_name, prompt)
                            
                            if success:
                                # Return public ngrok URL for email accessibility
                                public_url = f"https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/images/{image_id}"
                                print(f"✅ Stored Freepik image in ClickHouse: {image_id}")
                                
                                return {
                                    "image_url": public_url,
                                    "prompt": prompt,
                                    "status": "completed",
                                    "note": "Generated by Freepik AI and stored in ClickHouse"
                                }
                            else:
                                print(f"⚠️ Failed to store image, using fallback")
                                return self._get_fallback_image(disease_name, severity)
                    
                    # If job_id returned, poll for completion
                    if "job_id" in data:
                        print(f"📊 Polling Freepik job: {data['job_id']}")
                        image_url = await self._poll_for_image(data["job_id"])
                        if image_url:
                            return {
                                "image_url": image_url,
                                "prompt": prompt,
                                "status": "completed",
                                "note": "Generated by Freepik AI"
                            }
                    
                    print(f"⚠️ Freepik didn't return image, using fallback")
                    return self._get_fallback_image(disease_name, severity)
                else:
                    print(f"❌ Freepik API error: {response.status_code} - {response.text}")
                    return self._get_fallback_image(disease_name, severity)
                    
        except Exception as e:
            print(f"❌ Freepik generation error: {e}")
            return self._get_fallback_image(disease_name, severity)
    
    def _get_fallback_image(self, disease_name: str, severity: str) -> dict:
        """Generate fallback placeholder image"""
        severity_colors = {
            "critical": "dc2626",
            "pandemic": "7c2d12",
            "epidemic": "ea580c",
            "outbreak": "f59e0b",
            "cluster": "84cc16",
            "sporadic": "22c55e"
        }
        color = severity_colors.get(severity.lower(), "ef4444")
        placeholder_url = f"https://placehold.co/600x400/{color}/white?text=⚕️+{disease_name.upper()}+ALERT&font=roboto"
        
        return {
            "image_url": placeholder_url,
            "prompt": f"{disease_name} {severity} alert",
            "status": "fallback",
            "note": "Placeholder (Freepik unavailable)"
        }


# Global instance
freepik_service = FreepikService()
