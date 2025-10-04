# Airia Custom Tool Creation - Official Documentation Guide

**Source:** Official Airia Documentation (explore.airia.com)
**For:** VitalSignal Backend Integration
**Time:** 15-20 minutes

---

## Prerequisites

### ✅ Current Status - READY!

1. **Backend running:** ✅
   - FastAPI server: http://localhost:8000
   - Status: Active

2. **ngrok tunnel active:** ✅
   - Public URL: `https://chelsey-ideographical-emelia.ngrok-free.dev`
   - Dashboard: http://localhost:4040

3. **Your ngrok URL:** `https://chelsey-ideographical-emelia.ngrok-free.dev`

4. **Test endpoints manually:**
   ```bash
   # Test Get Users
   curl https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users
   
   # Test Personalize
   curl -X POST https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "demo_maria",
       "alert": {
         "alert_id": "test_001",
         "title": "Dengue Outbreak",
         "description": "500 cases",
         "disease": "dengue",
         "location": "São Paulo, Brazil",
         "severity": "outbreak",
         "published_at": "2025-10-04T15:00:00Z"
       }
     }'
   ```

---

## TOOL #1: Get VitalSignal Users

### Step 1: Navigate to Create Tool

1. In Airia, go to **Tools** (in project navigation)
2. Click **"Create New Tool"**
3. Select **"Custom API Tool"**

### Step 2: Fill Tool Definition

**According to Airia docs, you'll see these fields:**

#### **Tool Name**
```
Get VitalSignal Users
```

#### **Tool Purpose** 
*(This is treated as a PROMPT - tells the AI when to use this tool)*

```
Use this tool to retrieve the complete list of VitalSignal users. 

Call this tool FIRST before personalizing any health alerts.

This tool returns an array of user objects containing:
- user_id: unique identifier (required for personalization)
- name: user's full name
- email: contact email
- age: user's age
- location: user's current location as "City, Country"
- health_conditions: array of medical conditions with severity
- family_members: array with names, relationships, and locations
- travel_plans: array of upcoming trips with destinations and dates
- preferences: notification preferences and risk tolerance

Use the returned user_id values to call the "Personalize Risk Assessment" tool for each user.
```

#### **API Endpoint**

Select dropdown: **GET**

URL:
```
https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users
```

#### **Headers**

Click **"+ Add Header"**:

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |

#### **Body**

Leave empty (GET requests don't have a body)

#### **Authentication**

According to docs, select: **None** (our API doesn't require auth for demo)

### Step 3: Save Tool

1. Click **"Save"** to add to your tool library
2. Look for a **"Test"** button to verify
3. Expected result: JSON array with 3 users (Maria, John, Sarah)

---

## TOOL #2: Personalize Risk Assessment

### Step 1: Create New Tool

1. Go to **Tools** → **"Create New Tool"**
2. Select **"Custom API Tool"**

### Step 2: Fill Tool Definition

#### **Tool Name**
```
Personalize Risk Assessment
```

#### **Tool Purpose**
*(Critical - tells AI when and how to use this tool)*

```
Use this tool to calculate personalized health risk assessment for a specific user and health alert.

WHEN TO USE:
After retrieving users with "Get VitalSignal Users", call this tool for EACH user 
to get their personalized risk score.

REQUIRED INPUTS:
- user_id: User ID from the "Get VitalSignal Users" tool output
- alert_id: Unique alert identifier (e.g., "dengue_sp_001")
- title: Alert headline
- description: Detailed alert information
- disease: Disease name in lowercase (e.g., "dengue", "covid-19", "flu", "malaria")
- location: Affected location in format "City, Country" (e.g., "São Paulo, Brazil")
- severity: Exactly one of [pandemic, epidemic, outbreak, cluster, sporadic]
- published_at: ISO 8601 datetime (e.g., "2025-10-04T15:00:00Z")

RETURNS:
- risk_level: critical | high | medium | low | minimal
- risk_score: numeric score 0.0 to 1.0
- confidence: how confident the assessment is (0.0 to 1.0)
- reasoning: array of human-readable explanations
- recommended_actions: what actions to take
- needs_translation: whether translation needed
- needs_image: whether severity image needed
- priority: notification priority 1-10 (1 = highest)

IMPORTANT: Call this for ALL users to demonstrate personalization - 
different users will get different risk levels for the same alert.
```

#### **API Endpoint**

Select dropdown: **POST**

URL:
```
https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize
```

#### **Headers**

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |

#### **Body**

**According to Airia docs, you can use Tool Variables with `<variable/>` syntax:**

```json
{
  "user_id": "<user_id/>",
  "alert": {
    "alert_id": "<alert_id/>",
    "title": "<title/>",
    "description": "<description/>",
    "disease": "<disease/>",
    "location": "<location/>",
    "severity": "<severity/>",
    "published_at": "<published_at/>"
  }
}
```

**Important:** The `<variable/>` syntax tells Airia these are Tool Variables that the AI will fill in.

### Step 3: Define Tool Variables

According to the docs, you need to define variables separately.

Click **"Add Variable"** or similar button for each:

| Variable Name | Type | Description |
|--------------|------|-------------|
| `user_id` | String | User ID from Get Users tool |
| `alert_id` | String | Unique alert identifier |
| `title` | String | Alert headline |
| `description` | String | Detailed alert information |
| `disease` | String | Disease name (lowercase) |
| `location` | String | Location as "City, Country" |
| `severity` | String | One of: pandemic, epidemic, outbreak, cluster, sporadic |
| `published_at` | String | ISO 8601 datetime |

### Step 4: Authentication

Select: **None**

### Step 5: Save Tool

1. Click **"Save"**
2. Test with sample data:
   ```
   user_id: demo_maria
   alert_id: test_001
   title: Dengue Outbreak in São Paulo
   description: 500 confirmed cases reported
   disease: dengue
   location: São Paulo, Brazil
   severity: outbreak
   published_at: 2025-10-04T15:00:00Z
   ```
3. Expected: risk_level "high" with reasoning about diabetes and family

---

## Adding Tools to Your Agent

### Method 1: Add to AI Model (For Function Calling)

**From your screenshot - this is what you need:**

1. Open your **VitalSignal Agent** in Agent Canvas
2. Click on your **AI Model block** (the GPT-5 block)
3. In the right sidebar, click **"Tools"** tab
4. Click **"Add Tool"** or **"Select Tools"**
5. Check boxes for:
   - ☑️ Get VitalSignal Users
   - ☑️ Personalize Risk Assessment
6. Click **"Save"**

**The tools will appear in the model's footer and be available for the AI to call.**

### Method 2: Add as Workflow Actions (Advanced)

From the docs, you can also:
1. Drag tool from left sidebar onto canvas
2. It becomes a standalone action step
3. Connect with lines to define workflow
4. Configure parameters manually

**For your demo, use Method 1** - it's simpler and the AI decides when to call tools.

---

## Configure Agent Behavior

### Set the AI Model Prompt

Click on your **AI Model** block, find the **"Prompt"** or **"Instructions"** field:

```
You are VitalSignal, a personal health alert personalization AI agent.

WORKFLOW:
1. When you receive a health alert, FIRST use the "Get VitalSignal Users" tool
2. For EACH user returned, use the "Personalize Risk Assessment" tool with:
   - user_id from the Get Users tool output
   - alert information from the input (alert_id, title, description, disease, location, severity, published_at)

3. Present results as a comparison showing ALL users:
   - User name and key profile details
   - Risk Level (CRITICAL/HIGH/MEDIUM/LOW) - highlight this prominently
   - Risk Score (0-1 numeric)
   - Top 3 reasoning points explaining why
   - Recommended actions

IMPORTANT: 
- Show ALL three users to demonstrate personalization
- Different users WILL get different risk levels for the same alert
- This proves the system's autonomous decision-making

FORMAT OUTPUT as a clear comparison table or side-by-side view.
```

---

## Testing Your Agent

### Step 1: Test in Playground

1. Click **"Test"** button in Agent Canvas
2. Enter this test prompt:

```
Analyze this health alert:

Title: Dengue Outbreak in São Paulo
Description: Health authorities report 500 confirmed dengue fever cases in São Paulo, Brazil, with 3 fatalities. The outbreak is concentrated in the metropolitan area.
Disease: dengue
Location: São Paulo, Brazil
Severity: outbreak
Date: 2025-10-04T15:00:00Z
```

### Step 2: Expected Behavior

The AI should:
1. ✅ Call "Get VitalSignal Users" tool
2. ✅ Get back 3 users (Maria, John, Sarah)
3. ✅ Call "Personalize Risk Assessment" for Maria → HIGH risk (~0.75)
4. ✅ Call "Personalize Risk Assessment" for John → LOW risk (~0.15)
5. ✅ Call "Personalize Risk Assessment" for Sarah → CRITICAL risk (~0.90)
6. ✅ Display comparison showing different outcomes

### Step 3: Verify Results

**Maria (Expected HIGH):**
- Risk Score: ~0.70-0.80
- Reasoning: Diabetes increases vulnerability, Family in São Paulo

**John (Expected LOW):**
- Risk Score: ~0.10-0.20
- Reasoning: Healthy, No connections to affected area

**Sarah (Expected CRITICAL):**
- Risk Score: ~0.85-0.95
- Reasoning: Pregnancy high risk, Traveling to São Paulo in 10 days

---

## Tool Variables - How They Work

**From Airia Docs:**

When you use `<variable/>` syntax in the Body:
- The AI automatically extracts values from the conversation
- Variables are substituted when the tool is called
- You can see available variables in autocomplete

**Example:**
```json
{
  "user_id": "<user_id/>",
  "alert": {
    "disease": "<disease/>"
  }
}
```

When user says "Check dengue outbreak for Maria":
- AI sets `user_id` = "demo_maria"
- AI sets `disease` = "dengue"

---

## Best Practices (From Airia Docs)

### ✅ Naming Convention
Use clear, descriptive names:
- ✅ "Get VitalSignal Users"
- ✅ "Personalize Risk Assessment"
- ❌ "API Call 1"
- ❌ "User Tool"

### ✅ Tool Purpose Field
Treat this as a **prompt**. Be very specific about:
- When to use the tool
- What inputs it needs
- What it returns
- How the AI should use the output

### ✅ Error Handling
- Include clear error messages
- Test with both valid and invalid data
- Have fallback behaviors

---

## Troubleshooting

### "Tool not found" or "Tool not available"

**Cause:** Tool not added to AI Model

**Fix:**
1. Click AI Model block
2. Go to Tools tab
3. Select your tools
4. Save agent

### "Connection refused" or "Cannot connect to API"

**Cause:** ngrok tunnel down or wrong URL

**Fix:**
```bash
# Check ngrok is running
# Look for: Forwarding https://abc123.ngrok.io -> http://localhost:8000

# If ngrok stopped, restart:
ngrok http 8000

# Update tools with new URL
```

### "Invalid JSON" or "Bad Request"

**Cause:** Request body format incorrect

**Fix:**
- Check Tool Variable syntax: `<variable/>` not `{{variable}}`
- Verify JSON syntax in Body field
- Test endpoint manually with curl

### AI doesn't call tools

**Cause:** Tool Purpose not clear enough

**Fix:**
- Make Tool Purpose very explicit
- Use phrases like "Use this tool when..."
- Update AI Model prompt to mention tools

### "Timeout" error

**Cause:** API not responding

**Fix:**
- Check FastAPI server is running
- Test: `curl http://localhost:8000/health`
- Check server logs for errors
- Increase timeout if needed

---

## Authentication Methods Available

According to Airia docs, these auth types are supported:
- **None** (what we're using)
- Bearer Token
- Basic Authentication
- API Key (header or query parameter)
- OAuth (Google, Microsoft, Salesforce, X)

For our demo, we use **None** because our API doesn't require authentication.

---

## Quick Reference

### Your URLs
```
ngrok Public: https://chelsey-ideographical-emelia.ngrok-free.dev

Tool 1 Full URL: https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/users (GET)
Tool 2 Full URL: https://chelsey-ideographical-emelia.ngrok-free.dev/api/v1/personalize (POST)

Local API Docs: http://localhost:8000/docs
ngrok Dashboard: http://localhost:4040
```

### Variable Syntax
```json
Airia: <variable/>
NOT: {{variable}}
NOT: {variable}
```

### Tool Addition Steps
```
1. Tools → Create New Tool → Custom API Tool
2. Fill: Name, Purpose, Endpoint, Headers, Body, Auth
3. Define Tool Variables
4. Save to library
5. Add to Agent: Model block → Tools tab → Select tools
6. Configure Agent prompt
7. Test in Playground
```

---

## Next Steps

1. ✅ Verify backend is running
2. ✅ Get ngrok URL
3. ✅ Create Tool #1 (Get Users)
4. ✅ Test Tool #1
5. ✅ Create Tool #2 (Personalize)
6. ✅ Test Tool #2
7. ✅ Add both tools to AI Model
8. ✅ Configure Agent prompt
9. ✅ Test full workflow
10. → Prepare demo
11. → Submit to DevPost

---

## Summary

**Key Differences from Generic Guides:**
- ✅ Variable syntax: `<variable/>` (from official docs)
- ✅ Tool Purpose is a prompt field (from official docs)
- ✅ Tools added via Model block's Tools tab (from your screenshot)
- ✅ No HTTP Request pre-built tool - use Custom API Tool (from docs)

**You have everything you need. The backend is solid. Follow this guide to connect Airia to your API.**

🚀 Time to integrate!
