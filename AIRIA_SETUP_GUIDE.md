# Airia Setup Guide - Step by Step

**Time Estimate:** 20-30 minutes
**Goal:** Create an Airia agent that orchestrates VitalSignal workflow

---

## Prerequisites

- [x] Airia account access
- [x] Airia API key: `ak-MjUyMDY0NDQ1MHwxNzU5NTg0OTgwNjM1fHRpLVQzSmlhWFF0VDNCbGJpQlNaV2RwYzNSeVlYUnBiMjR0VUhKdlptVnpjMmx2Ym1Gc3wxfDIzNDY5ODg0ODYg`
- [ ] ngrok URL (see NGROK_SETUP_GUIDE.md)

---

## Option A: Simplified Integration (RECOMMENDED)

**Architecture:**
```
Airia Agent
  ↓
1. Structify Tool → Get health alerts
  ↓
2. HTTP Request Tool → Call our API for each user
     URL: <ngrok-url>/api/v1/personalize
  ↓
3. Display results
```

### Step 1: Create New Project

1. Log into Airia platform at https://airia.ai/
2. Click **"New Project"** or select existing project
3. Name it: `VitalSignal Health Guardian`
4. Click **"Create"**

### Step 2: Create New Agent

1. Inside your project, click **"Agents"** tab
2. Click **"New Agent"**
3. Name your agent: `VitalSignal Orchestrator`
4. Click **"Create"**

You should now see a canvas workspace.

### Step 3: Add Tools to Canvas

**From the left sidebar, drag these nodes onto the canvas:**

#### Node 1: Trigger/Input
- Type: **Input Node** or **Manual Trigger**
- Purpose: Start the workflow
- Configuration: Accept text input (health alert description)

#### Node 2: Structify (Web Scraping)
- Type: **Structify Tool** (if available in tool library)
- OR: **HTTP Request Tool** with these settings:
  - **URL:** `https://api.structify.ai/v1/scrape`
  - **Method:** POST
  - **Headers:**
    ```json
    {
      "Authorization": "Bearer gomez-orbit-ai",
      "Content-Type": "application/json"
    }
    ```
  - **Body:**
    ```json
    {
      "url": "https://www.who.int/emergencies/disease-outbreak-news",
      "extract_fields": ["title", "description", "location", "disease"]
    }
    ```

#### Node 3: Get Users List
- Type: **HTTP Request Tool**
- **Name:** `Get VitalSignal Users`
- **URL:** `<YOUR_NGROK_URL>/api/v1/users`
- **Method:** GET
- **Headers:**
  ```json
  {
    "Content-Type": "application/json"
  }
  ```

#### Node 4: For Each User Loop
- Type: **Loop Node** or **Iterator**
- **Input:** Users array from Node 3
- **Purpose:** Process each user individually

#### Node 5: Personalize Risk (Inside Loop)
- Type: **HTTP Request Tool**
- **Name:** `Calculate Personalized Risk`
- **URL:** `<YOUR_NGROK_URL>/api/v1/personalize`
- **Method:** POST
- **Headers:**
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **Body:**
  ```json
  {
    "user_id": "{{user.user_id}}",
    "alert": {
      "alert_id": "{{alert.id}}",
      "title": "{{alert.title}}",
      "description": "{{alert.description}}",
      "disease": "{{alert.disease}}",
      "location": "{{alert.location}}",
      "severity": "outbreak",
      "published_at": "{{now}}"
    }
  }
  ```

#### Node 6: Conditional Branch
- Type: **If/Else Node** or **Filter**
- **Condition:** `risk_score.risk_level == "high" OR risk_score.risk_level == "critical"`

#### Node 7: Send Notification (Inside True Branch)
- Type: **SendGrid Tool** (if available) or **HTTP Request**
- **Purpose:** Send email for high-risk users
- **Config:** Use SendGrid API with personalized message

#### Node 8: Output/Display
- Type: **Output Node**
- **Purpose:** Display all risk assessments
- **Format:** JSON array of results

### Step 4: Connect the Nodes

Using the **line drawing tool**, connect nodes in this order:

```
[Trigger] → [Structify] → [Get Users] → [Loop] → [Personalize] → [Conditional]
                                            ↓
                                    [Send Notification] → [Output]
```

### Step 5: Configure Variables

In each HTTP Request node:
- Replace `<YOUR_NGROK_URL>` with actual ngrok URL
- Use variable syntax: `{{variable_name}}` for dynamic values

### Step 6: Save & Test

1. Click **"Save Changes"** in top right
2. Click **"Test"** button
3. In the test panel, enter a sample alert:
   ```
   Dengue outbreak reported in São Paulo, Brazil. 500 cases confirmed.
   ```
4. Click **"Run"**
5. Watch the execution logs in the debug panel

### Step 7: Generate API Endpoint

1. Click **Settings** icon (top navigation)
2. Select **"Interfaces"**
3. Click **"View API Info"** next to API interface
4. Copy the API endpoint URL
5. Generate API key:
   - Click **"View API Keys"**
   - Click **"New API Key"**
   - Name: `VitalSignal Demo`
   - Scope: Current project
   - Click **"Create"**
   - **COPY THE KEY** (you won't see it again)

### Step 8: Publish

1. Click **"Publish"** button (top right)
2. Confirm publication
3. Your agent is now live!

---

## Option B: Full Orchestration (If Time Permits)

**More complex - Airia calls each external tool separately:**

Additional nodes to add:
- **PhenoML Enrichment** (HTTP Request to PhenoML API)
- **DeepL Translation** (HTTP Request to DeepL API)
- **Freepik Image Generation** (HTTP Request to Freepik API)

This requires more conditional logic and error handling. Only attempt if Option A works smoothly.

---

## Troubleshooting

### "Tool not found"
- Use **HTTP Request Tool** as universal fallback
- All external APIs can be called via HTTP Request

### "Authentication failed"
- Check API keys in .env file match your configuration
- Ensure ngrok tunnel is running

### "Connection refused"
- Verify ngrok URL is correct and active
- Test the endpoint manually in browser: `<ngrok-url>/health`

### "Rate limit exceeded"
- Reduce test frequency
- Use demo data instead of real scraping

---

## Demo Preparation

Before your presentation:

1. **Test the full flow** with real data
2. **Screenshot the canvas** (for backup slides)
3. **Have the debug logs open** (shows autonomy in action)
4. **Prepare 3 sample users:**
   - Maria (high risk)
   - John (low risk)
   - Sarah (critical risk)

---

## Quick Reference

**Airia Platform:** https://airia.ai/
**Airia Docs:** https://explore.airia.com/
**Your API Key:** `ak-MjUyMDY0NDQ1MHwxNzU5NTg0OTgwNjM1fHRpLVQzSmlhWFF0VDNCbGJpQlNaV2RwYzNSeVlYUnBiMjR0VUhKdlptVnpjMmx2Ym1Gc3wxfDIzNDY5ODg0ODYg`
**VitalSignal API Base:** `<ngrok-url>/api/v1`

---

## Next Steps

Once Airia is configured:
1. Test with demo users
2. Verify different outcomes for different users
3. Capture screenshots for presentation
4. Prepare 3-minute demo script
