# Demo Flow: Sauce AI Test Authoring + Mobile RDC Testing

This guide walks through the two demo flows we built and tested:

1. **AI Test Authoring (Web)** — Sauce's AI generates Selenium tests from natural language intent, runs them on VDC (Virtual Device Cloud), and shows results.
2. **Hand-written Appium Tests (Mobile)** — pytest + Appium tests run on real Android devices (Pixel 8) via Sauce RDC (Real Device Cloud) with Sauce Connect tunneling to localhost.

---

## 🎬 Demo at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│  Flow 1: AI Test Authoring (sprint-3 branch)                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Natural     │───▶│  Sauce AI    │───▶│  Sauce VDC       │  │
│  │  Language    │    │  generates   │    │  (Chrome/Win11)  │  │
│  │  Intent      │    │  Selenium    │    │  test runs       │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│         │                                              │        │
│         │          Serveo public tunnel               │        │
│         └──────────────────────────────────────────────┘        │
│                          localhost:3000 (React frontend)        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Flow 2: Mobile Appium (sprint-2-mobile branch)                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  pytest      │───▶│  Sauce       │───▶│  Sauce RDC       │  │
│  │  + Appium    │    │  Connect     │    │  (Pixel 8 real   │  │
│  │  tests       │    │  tunnel      │    │  device)         │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│         │                                              │        │
│         │          --proxy-localhost allow            │        │
│         └──────────────────────────────────────────────┘        │
│                          localhost:8000 (FastAPI backend)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisites

| Requirement | Notes |
|---|---|
| Sauce Labs account | With RDC access for mobile |
| `SAUCE_USERNAME` / `SAUCE_ACCESS_KEY` | From **Account → User Settings** |
| `sc` (Sauce Connect) | `brew install --cask sauce-connect` |
| `jq` | `brew install jq` |
| Python 3.11+ | For pytest + Appium |
| Node.js + npm | For React frontend build |

Set credentials:

```bash
export SAUCE_USERNAME="your-username"
export SAUCE_ACCESS_KEY="your-access-key"
export SAUCE_REGION="us-west-1"
```

---

## 🌿 Branch Overview

| Branch | Purpose | Key Stack |
|---|---|---|
| `sprint-3` | Web AI Authoring demo | Docker (React + FastAPI + PostgreSQL + Temporal) |
| `sprint-2-mobile` | Mobile Appium demo | Bare uvicorn backend, Android app, pytest+Appium |

> ⚠️ **Critical:** These branches conflict on port 8000. Always `docker-compose down` before switching from sprint-3 to sprint-2-mobile.

---

# Flow 1: AI Test Authoring (Web)

## Step 1 — Switch to sprint-3 and start services

```bash
git checkout sprint-3

# If coming from sprint-2-mobile, stop any bare backend first
pkill -f uvicorn 2>/dev/null

# Start Docker stack
docker-compose up -d backend db frontend
sleep 10

# Seed products + create test user
python3 scripts/seed_database.py
curl -s -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

Verify: http://localhost:3000 shows the login page.

## Step 2 — Expose localhost via Serveo tunnel

The AI test runner lives in Sauce's cloud and needs a public URL to reach your local frontend.

```bash
# Terminal 1 — frontend tunnel
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 \
  -R 80:localhost:3000 serveo.net
# Wait for "Forwarding HTTP traffic from https://xxxx.serveousercontent.com"

# Terminal 2 — backend tunnel
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 \
  -R 80:localhost:8000 serveo.net
# Wait for "Forwarding HTTP traffic from https://yyyy.serveousercontent.com"
```

Copy both URLs. Update the frontend's `REACT_APP_API_URL` to point to the backend tunnel:

```bash
cd frontend-web
REACT_APP_API_URL="https://yyyy.serveousercontent.com" npm run build
cd ..
npx serve -s frontend-web/build -l 3000 &
```

## Step 3 — Run AI Test Authoring

The script at `scripts/sauce_ai_web.sh` handles the full flow: generate → poll → run.

```bash
# Update the script with your current Serveo frontend URL
# (replace https://661dd48d3638afae-184-23-57-194.serveousercontent.com/)

scripts/sauce_ai_web.sh \
  "DreamDemo Web - Login and Browse" \
  "Login with test@example.com and password testpassword123, then verify the page shows Our Products section" \
  "DreamDemo-AI-Web-Build-$(date +%s)"
```

**What happens:**
1. POST to `/v1/ai-authoring/testcases/generate` with your intent
2. Poll `/v1/ai-authoring/testcases/generate/{taskId}` until `COMPLETED`
3. POST to `/v1/ai-authoring/testcases/{id}/run` to execute on Sauce VDC

**Chrome popup suppression** (already baked into the script):
```json
"goog:chromeOptions": {
  "args": ["--disable-notifications", "--disable-geolocation"],
  "prefs": {
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.geolocation": 2
  }
}
```

This prevents the "Allow device access?" popup from appearing.

## Step 4 — View results

```bash
# List recent VDC jobs
curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/rest/v1/$SAUCE_USERNAME/jobs?limit=5" | \
  jq '.[] | {id, name, passed, status}'

# Or open in browser
open "https://app.saucelabs.com/tests/"
```

**Expected result:** The AI-generated test logs in, scrolls to products, and asserts "Our Products" heading is visible.

---

# Flow 2: Mobile Appium Tests (RDC)

## Step 1 — Switch to sprint-2-mobile

```bash
# CRITICAL: Stop Docker from sprint-3 first
docker-compose down -v 2>/dev/null || true

git checkout sprint-2-mobile

# Start the bare Python backend (NOT Docker)
backend/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 --port 8000 --log-level info > backend.log 2>&1 &
sleep 3
curl -s http://localhost:8000/ | head -1
# → {"message":"Welcome to the Dream Demo Flower Shop API!"}
```

## Step 2 — Start Sauce Connect tunnel

```bash
export SAUCE_TUNNEL_NAME="demo-tunnel-$(date +%s)"
export SAUCE_APP_ID="storage:94eb7fcd-c35f-47d0-814d-627ce0e35aed"

sc run -u "$SAUCE_USERNAME" -k "$SAUCE_ACCESS_KEY" \
  -r us-west-1 -i "$SAUCE_TUNNEL_NAME" \
  --proxy-localhost allow \
  --log-file sc-demo.log
```

Wait for: `Sauce Connect is up, you may start your tests`

Then **wait 60 more seconds** for tunnel propagation:

```bash
sleep 60
```

> ⚠️ This delay is required — Sauce Labs needs time to register the tunnel globally before the Pixel 8 can reach it.

## Step 3 — Run the tests

```bash
pytest tests-e2e/test_two_specific.py \
  -k "test_successful_login or test_add_product_to_cart" -v
```

**What these tests do:**
- `test_successful_login` — Logs in with `test@example.com` / `testpassword123`, verifies home screen appears
- `test_add_product_to_cart` — Logs in, finds "Rose Bouquet", clicks "Add to Cart", verifies cart shows 1 item

**Auto-granted permissions** (no popup handling needed):
The fixture includes `autoGrantPermissions: True` so Android never asks for location/camera/storage.

## Step 4 — Verify results

```bash
# Check RDC jobs (should show "consolidated_status": "passed")
curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/v1/rdc/jobs?limit=2" | \
  jq '.entities[] | {id, name, consolidated_status}'
```

Or open https://app.saucelabs.com → **Automated** → **Test Results** → filter by "Real Device".

---

## 🔧 Key Fixes Applied

| Problem | Fix |
|---|---|
| Android permission popup ("Allow DreamDemo to access device location?") | `autoGrantPermissions: True` in UiAutomator2Options |
| Chrome permission popup in AI tests | `--disable-notifications` + prefs in `goog:chromeOptions` |
| Tunnel not reachable from device | `sleep 60` after "Sauce Connect is up" |
| Backend port conflict (sprint-3 vs sprint-2) | Always `docker-compose down` before switching branches |
| RDC jobs not marked as passed | `driver.execute_script("sauce:job-result=passed")` in fixture teardown |
| Login failing | Backend must have test user in SQLite DB |
| No products to add to cart | Seed DB with `curl -X POST /products/` or `seed_database.py` |

---

## 🎤 Suggested Demo Script (8 minutes)

| Time | Action | Branch | Talking Point |
|---|---|---|---|
| 0:00 | `git checkout sprint-2-mobile` | sprint-2-mobile | "First, let's see hand-written Appium tests on a real Pixel 8" |
| 0:30 | Start backend + Sauce Connect | sprint-2-mobile | "Backend runs locally, tunnel bridges to Sauce cloud" |
| 1:30 | `pytest test_two_specific.py -k test_successful_login` | sprint-2-mobile | "Real device, real app, real API calls through the tunnel" |
| 2:30 | Show Sauce Labs RDC job as "passed" | sprint-2-mobile | "Job auto-reports as passed — no manual clicking" |
| 3:00 | `git checkout sprint-3` | sprint-3 | "Now let's see AI write tests for us" |
| 3:30 | `docker-compose up -d` + Serveo tunnels | sprint-3 | "Same app, but now Sauce AI generates the test from a sentence" |
| 4:30 | `scripts/sauce_ai_web.sh "Login and Browse" ...` | sprint-3 | "The AI decides: click Continue, enter email, enter password, click Login, assert products" |
| 5:30 | Show AI-generated test steps in Sauce UI | sprint-3 | "Every step has a screenshot — you can debug the AI's reasoning" |
| 6:00 | Run the full `test_add_product_to_cart` too | sprint-2-mobile | "And the mobile tests cover the same flow with real touch events" |
| 7:00 | Side-by-side: AI-authored web vs hand-written mobile | both | "Two approaches, one platform. AI for exploration, code for precision." |

---

## 🧰 One-Command Setup

```bash
# --- Flow 1: AI Authoring (sprint-3) ---
git checkout sprint-3
docker-compose up -d backend db frontend
sleep 15
python3 scripts/seed_database.py
curl -s -X POST http://localhost:8000/users/ -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
# Start Serveo tunnels in separate terminals, then:
scripts/sauce_ai_web.sh "DreamDemo Web - Login and Browse" \
  "Login with test@example.com and password testpassword123, verify Our Products section" \
  "DreamDemo-AI-$(date +%s)"

# --- Flow 2: Mobile RDC (sprint-2-mobile) ---
docker-compose down -v
git checkout sprint-2-mobile
backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3
sc run -u "$SAUCE_USERNAME" -k "$SAUCE_ACCESS_KEY" -r us-west-1 \
  -i "demo-$(date +%s)" --proxy-localhost allow --log-file sc.log &
sleep 90  # 30s for tunnel up + 60s propagation
pytest tests-e2e/test_two_specific.py -k "test_successful_login or test_add_product_to_cart" -v
```

---

## 📚 References

- [`scripts/sauce_ai_web.sh`](./scripts/sauce_ai_web.sh) — AI test authoring runner
- [`tests-e2e/test_two_specific.py`](./tests-e2e/test_two_specific.py) — Mobile Appium tests
- [`tests-e2e/conftest_android.py`](./tests-e2e/conftest_android.py) — Sauce RDC fixture with autoGrantPermissions
- Sauce AI Authoring API: `https://api.us-west-1.saucelabs.com/v1/ai-authoring`
- Sauce RDC jobs API: `https://api.us-west-1.saucelabs.com/v1/rdc/jobs`
