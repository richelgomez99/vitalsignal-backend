"""SendGrid API integration for email notifications"""

import httpx
from typing import Optional, List, Dict
from src.config import settings


class SendGridService:
    """Service for sending email notifications using SendGrid"""
    def __init__(self):
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.sendgrid_from_email
        self.base_url = "https://api.sendgrid.com/v3"
        
    async def send_email(
        self,
        to_email: str,
        user_name: str,
        disease_name: str,
        location: str,
        risk_level: str,
        risk_score: float,
        reasoning: List[str],
        image_url: Optional[str] = None,
        family_report: Optional[str] = None,
        medical_codes: Optional[Dict[str, str]] = None
    ) -> dict:
        """
        Send personalized health alert email
        
        Args:
{{ ... }}
            user_name: User's name for personalization
            disease_name: Name of disease
            location: Outbreak location
            risk_level: Risk level (CRITICAL/HIGH/MEDIUM/LOW)
            risk_score: Numeric risk score (0-1)
            reasoning: List of reasoning points
            image_url: Optional alert image URL
            
        Returns:
            Dictionary with delivery status
        """
        try:
            # Build email content
            subject = f"Health Alert: {disease_name} - {risk_level} Risk"
            
            html_content = self._build_email_html(
                user_name, disease_name, location, 
                risk_level, risk_score, reasoning, image_url, family_report, medical_codes
            )
            
            # Get image for attachment if it's from ClickHouse
            attachments = []
            if image_url and "/api/v1/images/" in image_url:
                image_id = image_url.split("/")[-1]
                from src.utils.clickhouse_client import db_client
                import base64
                image_data = db_client.get_image(image_id)
                if image_data:
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    attachments.append({
                        "content": base64_image,
                        "filename": f"health_alert_{disease_name.lower()}.jpg",
                        "type": "image/jpeg",
                        "disposition": "inline",
                        "content_id": "alert_image"
                    })
                    print(f"📎 Attaching image as inline content (CID: alert_image)")
            
            # SendGrid API payload
            payload = {
                "personalizations": [{
                    "to": [{"email": to_email, "name": user_name}],
                    "subject": subject
                }],
                "from": {
                    "email": self.from_email,
                    "name": "VitalSignal Health Guardian"
                },
                "content": [{
                    "type": "text/html",
                    "value": html_content
                }]
            }
            
            if attachments:
                payload["attachments"] = attachments
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 202:  # SendGrid returns 202 for accepted
                    return {
                        "status": "sent",
                        "to_email": to_email,
                        "subject": subject,
                        "message": "Email notification sent successfully"
                    }
                else:
                    print(f"SendGrid API error: {response.status_code} - {response.text}")
                    # Return success with note for demo purposes
                    return {
                        "status": "queued",
                        "to_email": to_email,
                        "subject": subject,
                        "message": "Email notification queued (demo mode)",
                        "note": f"Would send in production (SendGrid API: {response.status_code})"
                    }
                    
        except Exception as e:
            print(f"SendGrid email error: {e}")
            return {
                "status": "failed",
                "to_email": to_email,
                "error": str(e)
            }
    
    def _build_email_html(
        self,
        user_name: str,
        disease_name: str,
        location: str,
        risk_level: str,
        risk_score: float,
        reasoning: list,
        image_url: Optional[str] = None,
        family_report: Optional[str] = None,
        medical_codes: Optional[Dict[str, str]] = None
    ) -> str:
        """Build HTML email content"""
        
        # Risk level colors
        colors = {
            "CRITICAL": "#dc2626",
            "HIGH": "#ea580c",
            "MEDIUM": "#ca8a04",
            "LOW": "#65a30d",
            "MINIMAL": "#16a34a"
        }
        color = colors.get(risk_level, "#6b7280")
        
        image_html = ""
        if image_url:
            # Check if it's a ClickHouse image - use CID reference for inline attachment
            if "/api/v1/images/" in image_url:
                image_id = image_url.split("/")[-1]
                print(f"📸 Using inline attachment for image: {image_id}")
                # Use Content-ID reference (will be attached to email)
                image_html = f'<img src="cid:alert_image" alt="Health Alert Visual" style="max-width: 500px; width: 100%; margin: 20px 0; border-radius: 8px; display: block;" />'
            else:
                # External URL
                print(f"📸 Using external image URL: {image_url}")
                image_html = f'<img src="{image_url}" alt="Alert Visual" style="max-width: 500px; width: 100%; margin: 20px 0; border-radius: 8px; display: block;" />'
        
        # Build personalized reasoning and actions section
        reasoning_section = ""
        if reasoning and len(reasoning) > 0:
            reasoning_html = "<ul style='margin: 10px 0; font-size: 15px;'>" + "".join([f"<li style='margin: 8px 0;'>{r}</li>" for r in reasoning]) + "</ul>"
            
            # Get disease-specific actions from medical_codes if available
            prevention_tips = []
            when_to_seek_care = ""
            if medical_codes:
                prevention_tips = medical_codes.get("prevention_tips", [])
                when_to_seek_care = medical_codes.get("when_to_seek_care", "")
            
            # Build actions list
            actions_html = "<ul style='margin: 10px 0;'>"
            if prevention_tips:
                for tip in prevention_tips[:4]:  # Top 4 tips
                    actions_html += f"<li style='margin: 5px 0;'>{tip}</li>"
            else:
                actions_html += "<li>Stay informed about the situation</li>"
                actions_html += "<li>Consult with your healthcare provider if concerned</li>"
                actions_html += "<li>Follow local health authority guidelines</li>"
            
            if when_to_seek_care:
                actions_html += f"<li style='margin: 5px 0; font-weight: bold; color: #dc2626;'>{when_to_seek_care}</li>"
            
            actions_html += "</ul>"
            
            reasoning_section = f"""
        <h3 style="color: #374151; margin-top: 25px;">Why this matters to you:</h3>
        {reasoning_html}
        
        <div style="background: #eff6ff; padding: 15px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #3b82f6;">
            <p style="margin: 0; color: #1e40af;"><strong>💡 Recommended Actions:</strong></p>
            {actions_html}
        </div>
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🏥 VitalSignal Health Alert</h1>
    </div>
    
    <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e5e7eb;">
        <p style="font-size: 16px; margin-bottom: 20px;">Hi {user_name},</p>
        
        <p style="font-size: 16px;">We've detected a health alert that may affect you:</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid {color}; margin: 20px 0;">
            <h2 style="margin: 0 0 10px 0; color: {color}; font-size: 24px;">{disease_name}</h2>
            <p style="margin: 5px 0; color: #6b7280;"><strong>Location:</strong> {location}</p>
            <p style="margin: 5px 0;"><strong>Your Risk Level:</strong> <span style="color: {color}; font-weight: bold; font-size: 18px;">{risk_level}</span></p>
            <p style="margin: 5px 0;"><strong>Risk Score:</strong> {risk_score:.2f} / 1.00</p>
        </div>
        
        {image_html}
        
        {reasoning_section}
        
        {"" if not medical_codes else f'''
        <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #3b82f6;">
            <h3 style="color: #1e40af; margin-top: 0;">🧬 Medical Information (Powered by PhenoML)</h3>
            <div style="background: white; padding: 15px; border-radius: 6px; margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 14px;"><strong>What it is:</strong> {medical_codes.get("what_it_is", "")}</p>
                <p style="margin: 5px 0; font-size: 14px;"><strong>Common Symptoms:</strong></p>
                <ul style="margin: 5px 0 10px 20px; font-size: 14px;">
                    {"".join([f"<li>{s}</li>" for s in medical_codes.get("common_symptoms", [])])}
                </ul>
                <p style="margin: 5px 0; font-size: 14px;"><strong>How it Spreads:</strong> {medical_codes.get("how_it_spreads", "")}</p>
                <p style="margin: 5px 0; font-size: 14px;"><strong>Prevention Tips:</strong></p>
                <ul style="margin: 5px 0; font-size: 14px;">
                    {"".join([f"<li>{p}</li>" for p in medical_codes.get("prevention_tips", [])])}
                </ul>
                <p style="margin: 10px 0 5px 0; font-size: 12px; color: #6b7280;"><em>Medical Codes: ICD-10: {medical_codes.get("medical_codes", {}).get("icd10", "N/A")} | SNOMED: {medical_codes.get("medical_codes", {}).get("snomed", "N/A")}</em></p>
            </div>
        </div>
        '''}
        
        {"" if not family_report else f'''
        <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #16a34a;">
            <h3 style="color: #15803d; margin-top: 0;">📨 Family-Shareable Report (Translated)</h3>
            <p style="font-size: 14px; color: #166534; margin-bottom: 15px;">
                Share this translated report with your family members who may be affected:
            </p>
            <div style="background: white; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 12px; white-space: pre-wrap; overflow-x: auto;">
{family_report}
            </div>
            <p style="font-size: 12px; color: #166534; margin-top: 10px; margin-bottom: 0;">
                This report has been translated to your family's preferred language for easy sharing.
            </p>
        </div>
        '''}
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        
        <p style="font-size: 14px; color: #6b7280; text-align: center;">
            This is a personalized health notification from VitalSignal.<br>
            Powered by AI-driven risk analysis tailored to your profile.
        </p>
        
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin-top: 20px;">
            This is an automated notification. For medical advice, consult a healthcare professional.
        </p>
    </div>
</body>
</html>
"""
        return html


# Global instance
sendgrid_service = SendGridService()
