#!/usr/bin/env python3
"""Quick test of Structify API to see what data we get"""

import httpx
import asyncio
import json
from src.config import settings


async def test_structify():
    """Test Structify API endpoints"""
    
    api_key = settings.structify_api_key
    base_url = "https://api.structify.ai"
    
    print(f"🔍 Testing Structify API...")
    print(f"API Key: {api_key[:20]}...")
    print()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Try different API endpoints
        endpoints = [
            "/v1/datasets",
            "/v1/jobs",
            "/v1/extractions",
            "/datasets",
            "/jobs"
        ]
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 Trying: {url}")
            
            try:
                response = await client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ SUCCESS! Response:")
                    print(json.dumps(response.json(), indent=2)[:1000])
                    break
                else:
                    print(f"Response: {response.text[:200]}")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_structify())
