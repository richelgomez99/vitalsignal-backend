# Airia Custom Tool Creation - Practical Guide

**Based on:** Official Airia documentation patterns
**For:** VitalSignal Backend Integration
**Time:** 15-20 minutes

---

## What You're Creating

**2 Custom API Tools:**
1. Get VitalSignal Users - Retrieves user list
2. Personalize Risk - Calculates personalized health risk

---

## Before You Start

### ✅ Prerequisites Checklist

- [ ] FastAPI server running: `uvicorn src.main:app --reload --port 8000`
- [ ] ngrok tunnel active: `ngrok http 8000`
- [ ] ngrok URL copied (example: `https://abc123.ngrok.io`)
- [ ] Test your API manually:

```bash
# Test 1: Get Users
curl https://YOUR-NGROK-URL.ngrok.io/api/v1/users

# Expected: JSON array with 3 users

# Test 2: Personalize
curl -X POST https://YOUR-NGROK-URL.ngrok.io/api/v1/personalize \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_maria",
    "alert": {
      "alert_id": "test_001",
      "title": "Dengue Outbreak",
      "description": "500 cases in São Paulo",
      "disease": "dengue",
      "location": "São Paulo, Brazil",
      "severity": "outbreak",
      "published_at": "2025-10-04T15:00:00Z"
    }
  }'

# Expected: Risk score with reasoning
```

---

## TOOL #1: Get VitalSignal Users

### Step 1: Navigate to Tool Creation

**In Airia Platform:**
1. Open your project/workspace
2. Look for **"Tools"** in the sidebar (under Integrations)
3. Click **"Create New Tool"** or **"+ Add Tool"** button
4. Select **"Custom Tool"** (not from library)

### Step 2: Fill Basic Information

Based on Airia's standard form (from Salesforce/Microsoft examples):

| Field Label | What to Enter |
|-------------|---------------|
| **Tool Name** | `Get VitalSignal Users` |
| **Description** | `Retrieves all VitalSignal users with health profiles, family locations, and travel plans for risk assessment` |
| **Category** (if exists) | `Custom` or `Data Retrieval` |

### Step 3: API Configuration

| Field Label | What to Enter | Your Value |
|-------------|---------------|------------|
| **API Type** (if exists) | REST API / HTTP Request | REST API |
| **Base URL** or **API Endpoint** | Your ngrok URL | `https://abc123.ngrok.io/api/v1/users` |
| **HTTP Method** / **Request Type** | GET | GET |
| **Content Type** (if exists) | application/json | application/json |

**Note:** Some forms combine Base URL + Path, others have one field. Use the full URL: `https://YOUR-NGROK-URL.ngrok.io/api/v1/users`

### Step 4: Headers (if there's a section)

If you see **"Headers"** or **"Request Headers"** section:

Click **"+ Add Header"**:

| Header Name | Header Value |
|-------------|--------------|
| Accept | application/json |
| Content-Type | application/json |

**If no headers section exists:** Skip - defaults are usually fine

### Step 5: Parameters

**Query Parameters:** Leave empty (this endpoint doesn't use any)

**Path Parameters:** Leave empty

**Request Body:** Leave empty (GET requests don't have body)

### Step 6: Authentication

Based on Airia docs, you'll see an **"Authentication"** dropdown:

| Field | Selection |
|-------|-----------|
| **Authentication Type** | None / No Authentication |
| **Credentials** | (Leave empty) |

Our API doesn't require authentication for the demo.

### Step 7: Response Configuration (if exists)

| Field | Value |
|-------|-------|
| **Expected Response Format** | JSON |
| **Success Status Code** | 200 |

### Step 8: Tool Instructions (Important!)

If there's a **"Tool Description for AI"** or **"How to Use"** field:

```
This tool retrieves the complete list of VitalSignal users.

WHEN TO USE:
Call this tool first before personalizing any health alerts.

RETURNS:
Array of user objects, each containing:
- user_id: unique identifier
- name: user's full name  
- email: contact email
- age: user's age
- location: "City, Country"
- health_conditions: array of medical conditions
- family_members: array with names and locations
- travel_plans: array of upcoming trips
- preferences: notification preferences

EXAMPLE OUTPUT:
[
  {
    "user_id": "demo_maria",
    "name": "Maria Silva",
    "health_conditions": [{"name": "diabetes"}],
    "family_members": [{"name": "Ana", "location": "São Paulo, Brazil"}]
  }
]

Use the returned user_ids to call the Personalize Risk Assessment tool.
```

### Step 9: Save Tool

1. Click **"Test"** button (if available) to verify it works
2. Expected result: JSON array with 3 users
3. Click **"Save"** or **"Create Tool"** button
4. Tool should now appear in your Tools library

---

## TOOL #2: Personalize Risk Assessment

### Step 1: Create New Tool

1. Go to **Tools** → **"Create New Tool"**
2. Select **"Custom Tool"**

### Step 2: Basic Information

| Field Label | What to Enter |
|-------------|---------------|
| **Tool Name** | `Personalize Risk Assessment` |
| **Description** | `Calculates personalized health risk score for a user based on alert. Returns risk level (Critical/High/Medium/Low), reasoning, and recommended actions.` |
| **Category** | `Custom` or `AI/ML` |

### Step 3: API Configuration

| Field Label | What to Enter | Your Value |
|-------------|---------------|------------|
| **API Type** | REST API / HTTP Request | REST API |
| **Base URL** or **API Endpoint** | Your ngrok URL + endpoint | `https://abc123.ngrok.io/api/v1/personalize` |
| **HTTP Method** | POST | POST |
| **Content Type** | application/json | application/json |

### Step 4: Headers

| Header Name | Header Value |
|-------------|--------------|
| Content-Type | application/json |
| Accept | application/json |

### Step 5: Request Parameters/Body

**This is the critical part for POST requests.**

#### Option A: If there's a JSON editor for "Request Body":

Paste this:

```json
{
  "user_id": "{{user_id}}",
  "alert": {
    "alert_id": "{{alert_id}}",
    "title": "{{title}}",
    "description": "{{description}}",
    "disease": "{{disease}}",
    "location": "{{location}}",
    "severity": "{{severity}}",
    "published_at": "{{published_at}}"
  }
}
```

The `{{variable}}` syntax tells Airia these are parameters the AI can fill in.

#### Option B: If there are individual "Parameter" fields:

Click **"+ Add Parameter"** for each:

| Parameter Name | Type | Required | Description |
|---------------|------|----------|-------------|
| user_id | String | Yes | User ID from Get Users tool |
| alert_id | String | Yes | Unique alert identifier |
| title | String | Yes | Alert headline |
| description | String | Yes | Alert details |
| disease | String | Yes | Disease name (e.g., dengue) |
| location | String | Yes | Location as "City, Country" |
| severity | String | Yes | One of: pandemic, epidemic, outbreak, cluster, sporadic |
| published_at | String | Yes | ISO datetime (e.g., 2025-10-04T15:00:00Z) |

#### Option C: If there's a "Sample Request" field:

```json
{
  "user_id": "demo_maria",
  "alert": {
    "alert_id": "dengue_sp_001",
    "title": "Dengue Outbreak in São Paulo",
    "description": "500 confirmed cases reported",
    "disease": "dengue",
    "location": "São Paulo, Brazil",
    "severity": "outbreak",
    "published_at": "2025-10-04T15:00:00Z"
  }
}
```

### Step 6: Authentication

| Field | Selection |
|-------|-----------|
| **Authentication Type** | None |

### Step 7: Response Configuration

| Field | Value |
|-------|-------|
| **Response Format** | JSON |
| **Success Status Code** | 200 |

### Step 8: Tool Instructions for AI

```
This tool calculates a personalized health risk assessment for a specific user and health alert.

WHEN TO USE:
After retrieving users with "Get VitalSignal Users", call this tool for each user 
to get their personalized risk assessment.

REQUIRED INPUTS:
- user_id: Get from "Get VitalSignal Users" tool output
- alert object with:
  - alert_id: unique ID (e.g., "dengue_sp_001")
  - title: alert headline
  - description: detailed information
  - disease: disease name (lowercase, e.g., "dengue", "covid-19", "flu")
  - location: format as "City, Country" (e.g., "São Paulo, Brazil")
  - severity: exactly one of [pandemic, epidemic, outbreak, cluster, sporadic]
  - published_at: ISO 8601 datetime (e.g., "2025-10-04T15:00:00Z")

RETURNS:
{
  "user": {user details},
  "risk_score": {
    "risk_level": "critical" | "high" | "medium" | "low" | "minimal",
    "risk_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "reasoning": [array of explanations],
    "recommended_actions": [array of actions],
    "needs_translation": boolean,
    "needs_image": boolean,
    "priority": 1-10
  }
}

EXAMPLE:
For Maria (diabetic, family in São Paulo) + Dengue alert in São Paulo:
- risk_level: "high"
- risk_score: ~0.75
- reasoning: ["Your health conditions (diabetes) increase vulnerability", 
              "Family members are in the affected area"]

Call this for ALL users to show different personalization outcomes.
```

### Step 9: Test & Save

1. Click **"Test"** button
2. Fill in test data:
   ```
   user_id: demo_maria
   alert_id: test_001
   title: Dengue Outbreak in São Paulo
   description: 500 cases reported
   disease: dengue
   location: São Paulo, Brazil
   severity: outbreak
   published_at: 2025-10-04T15:00:00Z
   ```
3. Verify result shows risk_level: "high" and reasoning
4. Click **"Save"** / **"Create Tool"**

---

## Adding Tools to Your Agent

### Method 1: Via Agent Canvas (What you showed in screenshot)

1. Open your **VitalSignal Agent** in the canvas
2. Click on your **AI Model block** (the GPT-5 block)
3. Right sidebar should appear
4. Click **"Tools"** tab (next to "Model")
5. Look for **"+ Add Tool"** or **"Select Tools"** button
6. Find your tools:
   - ☑️ Get VitalSignal Users
   - ☑️ Personalize Risk Assessment
7. Check both boxes
8. Click **"Apply"** or **"Save"**

### Method 2: Direct Assignment

Some Airia versions let you:
1. Drag tool from library onto canvas
2. Connect it to your AI Model block
3. Link nodes with lines

---

## Configuring How the AI Uses Your Tools

### Step 1: Set Agent Prompt

Click on your **AI Model** block, look for **"Prompt"** or **"Instructions"** field:

```
You are VitalSignal, a personal health alert personalization AI.

WORKFLOW:
1. When you receive a health alert, FIRST call "Get VitalSignal Users" 
2. For EACH user returned, call "Personalize Risk Assessment" with:
   - The user's user_id from step 1
   - The alert information provided

3. Display results as a comparison showing:
   - User name and age
   - Risk Level (CRITICAL/HIGH/MEDIUM/LOW) - make this prominent
   - Risk Score (0-1) 
   - Top 3 reasoning points
   - Recommended actions

IMPORTANT: Show ALL users to demonstrate personalization.
Different users should get DIFFERENT risk levels for the same alert.

FORMAT: Present as a clear comparison table or side-by-side cards.
```

### Step 2: Test in Playground

1. Click **"Test"** button in agent canvas
2. In the chat, enter:
   ```
   Analyze this health alert:
   
   Title: Dengue Outbreak in São Paulo
   Description: Health authorities report 500 confirmed dengue cases in São Paulo, Brazil
   Disease: dengue
   Location: São Paulo, Brazil
   Severity: outbreak
   Date: 2025-10-04
   ```

3. Expected behavior:
   - AI calls Get Users tool
   - AI calls Personalize for Maria → HIGH risk
   - AI calls Personalize for John → LOW risk
   - AI calls Personalize for Sarah → CRITICAL risk
   - AI displays comparison

---

## Troubleshooting

### "Tool Not Found" when testing

**Cause:** Tool not added to agent

**Fix:**
1. Click AI Model block → Tools tab
2. Select your custom tools
3. Save agent

### "Connection Refused" or "Cannot Connect"

**Cause:** ngrok tunnel down or wrong URL

**Fix:**
```bash
# Check ngrok is running
# Terminal should show: Forwarding https://abc123.ngrok.io -> http://localhost:8000

# If not running, start it:
ngrok http 8000

# Update tool with new URL if ngrok restarted
```

### "Invalid Request" or "400 Bad Request"

**Cause:** Request body format wrong

**Fix:**
- Check JSON syntax in tool configuration
- Verify all required fields are present
- Test manually with curl first

### "Timeout" error

**Cause:** API not responding or taking too long

**Fix:**
- Check FastAPI server is running: `http://localhost:8000/docs`
- Test endpoint manually
- Check server logs for errors

### AI doesn't call tools automatically

**Cause:** Prompt doesn't instruct to use tools

**Fix:**
- Update AI Model prompt to explicitly mention tools
- Use phrases like "Use the Get VitalSignal Users tool"
- Make workflow steps very clear

---

## Quick Reference: Your URLs

**Replace these when creating tools:**

```
Base API URL: https://YOUR-NGROK-URL.ngrok.io

Tool 1: https://YOUR-NGROK-URL.ngrok.io/api/v1/users
Tool 2: https://YOUR-NGROK-URL.ngrok.io/api/v1/personalize

Test locally: http://localhost:8000/docs
```

---

## Next Steps

1. ✅ Create both tools
2. ✅ Test each individually  
3. ✅ Add to agent
4. ✅ Configure agent prompt
5. → Test full workflow
6. → Prepare demo
7. → Polish presentation

**You're almost there! The backend is solid, tools connect the pieces together.**
