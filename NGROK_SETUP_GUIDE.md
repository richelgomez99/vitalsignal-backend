# ngrok Setup Guide - Step by Step

**Time Estimate:** 10 minutes
**Goal:** Expose your local FastAPI server to the internet for Airia integration

---

## What is ngrok?

ngrok creates a secure tunnel from a public URL to your local development server.
This lets Airia (or any external service) call your FastAPI endpoints without deploying to cloud.

**Example:**
- Your local server: `http://localhost:8000`
- ngrok public URL: `https://abc123.ngrok.io`
- Airia calls: `https://abc123.ngrok.io/api/v1/personalize`
- Request reaches: `http://localhost:8000/api/v1/personalize`

---

## Step 1: Create ngrok Account

1. Go to https://dashboard.ngrok.com/signup
2. Sign up with email or GitHub
3. Confirm your email
4. Log in to dashboard

---

## Step 2: Install ngrok (Mac)

**Option A: Using Homebrew (Recommended)**

```bash
# Install ngrok
brew install ngrok
```

**Option B: Manual Download**

```bash
# Download from website
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip

# Unzip
unzip ngrok-v3-stable-darwin-amd64.zip

# Move to /usr/local/bin
sudo mv ngrok /usr/local/bin/
```

**Verify Installation:**

```bash
ngrok help
```

You should see ngrok commands listed.

---

## Step 3: Authenticate ngrok

1. **Get your auth token:**
   - Go to https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your authtoken (looks like: `2a1b2c3d4e5f_6g7h8i9j0k1l2m3n4o5p`)

2. **Add token to ngrok:**

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with the actual token.

**Example:**
```bash
ngrok config add-authtoken 2a1b2c3d4e5f_6g7h8i9j0k1l2m3n4o5p
```

You should see: `Authtoken saved to configuration file`

---

## Step 4: Start Your FastAPI Server

**In Terminal 1:**

```bash
cd /Users/richelgomez/Documents/hackathon/vitalsignal-backend

# Install dependencies (if not done yet)
pip install -r requirements.txt

# Start server
uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this terminal running!**

---

## Step 5: Start ngrok Tunnel

**In Terminal 2 (NEW terminal window):**

```bash
ngrok http 8000
```

You should see:

```
ngrok

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**IMPORTANT: Copy the Forwarding URL**
- It will look like: `https://abc123.ngrok.io`
- This is your public URL!
- It changes every time you restart ngrok (unless you have a paid plan)

---

## Step 6: Test Your Tunnel

**In a new terminal or browser:**

```bash
# Test health endpoint
curl https://YOUR-NGROK-URL.ngrok.io/health
```

You should get a JSON response from your FastAPI server.

**Or open in browser:**
- Navigate to: `https://YOUR-NGROK-URL.ngrok.io/docs`
- You should see FastAPI's interactive API documentation

---

## Step 7: Monitor Traffic

ngrok provides a web interface to see all requests:

1. Open browser to: http://localhost:4040
2. You'll see:
   - All HTTP requests coming through ngrok
   - Request/response details
   - Replay functionality for testing

This is EXTREMELY useful for debugging!

---

## Step 8: Update Airia Configuration

**Take your ngrok URL and update Airia:**

1. In Airia canvas, find all HTTP Request nodes
2. Replace `<YOUR_NGROK_URL>` with your actual URL
3. Example:
   - Before: `<YOUR_NGROK_URL>/api/v1/personalize`
   - After: `https://abc123.ngrok.io/api/v1/personalize`

---

## Important Notes

### ⚠️ Free Tier Limitations

- **URL changes on restart:** Every time you stop/start ngrok, you get a new URL
- **2 hour session limit:** Connection may timeout (just restart)
- **No custom domain:** You get random subdomains like `abc123.ngrok.io`

**Workaround:** Keep ngrok running throughout your development session.

### ⚠️ Security

- ngrok URLs are public but obscure (hard to guess)
- Don't share your ngrok URL publicly
- Don't commit ngrok URLs to git
- For production, use proper deployment

### ✅ Best Practices

1. **Keep two terminals open:**
   - Terminal 1: FastAPI server (`uvicorn`)
   - Terminal 2: ngrok tunnel

2. **Use ngrok web interface** (localhost:4040)
   - Monitor all requests
   - Debug issues
   - Replay requests for testing

3. **Check CORS settings:**
   - Your FastAPI might need to allow ngrok domain
   - We'll handle this in the code

---

## Troubleshooting

### "ngrok: command not found"
```bash
# Verify installation
which ngrok

# If not found, reinstall
brew install ngrok
```

### "Failed to start tunnel"
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>

# Restart FastAPI
uvicorn src.main:app --reload --port 8000
```

### "Connection refused"
- Make sure FastAPI is running on port 8000
- Check that you're exposing the correct port: `ngrok http 8000`

### "Authentication failed"
```bash
# Re-add auth token
ngrok config add-authtoken YOUR_TOKEN
```

---

## Quick Reference Commands

```bash
# Start FastAPI server
uvicorn src.main:app --reload --port 8000

# Start ngrok tunnel
ngrok http 8000

# View ngrok web interface
open http://localhost:4040

# Test your endpoint
curl https://YOUR-URL.ngrok.io/health

# Stop ngrok (in Terminal 2)
Ctrl + C

# Stop FastAPI (in Terminal 1)
Ctrl + C
```

---

## Alternative: ngrok Configuration File

For convenience, create a persistent config:

```bash
# Edit ngrok config
ngrok config edit
```

Add this:

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN
tunnels:
  vitalsignal:
    proto: http
    addr: 8000
    inspect: true
```

Then start with:
```bash
ngrok start vitalsignal
```

---

## Next Steps

1. ✅ ngrok tunnel is running
2. ✅ You have a public URL
3. → Update Airia configuration with this URL
4. → Test the integration
5. → Monitor traffic in ngrok dashboard

**Your ngrok URL:** `https://__________.ngrok.io` (fill in after starting)

**Save this URL!** You'll need it for:
- Airia canvas configuration
- Testing API calls
- Demo presentation
