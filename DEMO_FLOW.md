# Demo Flow: MCP Server + Sauce AI Insights

This guide walks through a end‑to‑end demo of the Dream Demo project that ties together:

1. **Sauce Labs MCP servers** — let an AI assistant (Claude Desktop / Gemini CLI / Cursor) query your Sauce Labs account in natural language.
2. **Sauce RDC VS Code extension** — a live device & session browser pinned in your editor's sidebar.
3. **Sauce AI Insights** — Sauce's built‑in analytics + ML‑powered failure analysis surface for every test run.

The story you're telling: *"I run my tests on Sauce Labs, Sauce AI Insights tells me what broke and why, and my MCP‑connected AI assistant lets me investigate, triage, and act without leaving my editor."*

---

## 🎬 Demo at a Glance

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Dream Demo App  │────▶│   Sauce Labs     │────▶│  Sauce AI        │
│  (web + Android) │     │   (VDC + RDC)    │     │  Insights        │
└──────────────────┘     └────────┬─────────┘     └──────────────────┘
                                  │                         ▲
                                  │ REST API                │
                  ┌───────────────┼───────────────┐         │
                  ▼               ▼               ▼         │
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
         │ Sauce RDC    │ │ sauce-api-   │ │ Insights UI  │─┘
         │ VS Code ext. │ │ mcp servers  │ │ (browser)    │
         └──────┬───────┘ └──────┬───────┘ └──────────────┘
                │                │ MCP protocol
                │ in‑editor      ▼
                │         ┌──────────────────┐
                └────────▶│ AI Assistant     │
                          │ (Claude/Gemini)  │
                          └──────────────────┘
```

- Tests are executed against the Dream Demo app on Sauce Labs (web via VDC, Android via RDC).
- Results stream into **Sauce AI Insights** automatically.
- The **MCP server** exposes the Sauce REST API as tools the AI assistant can call.
- You ask questions in chat — the assistant calls MCP tools, summarizes results, and links you back into Insights for deep dives.

---

## ✅ Prerequisites

| Requirement | Notes |
|---|---|
| Docker Desktop | To run the Dream Demo locally |
| Sauce Labs account | With RDC access for the mobile portion |
| `SAUCE_USERNAME` / `SAUCE_ACCESS_KEY` | From **Account → User Settings** |
| `pipx` | `brew install pipx` |
| AI client | Claude Desktop **or** Gemini CLI **or** Cursor (any MCP‑capable client) |
| VS Code (or Cursor) | For the **Sauce RDC** extension |

Set credentials once in your shell:

```bash
export SAUCE_USERNAME="your-username"
export SAUCE_ACCESS_KEY="your-access-key"
export SAUCE_REGION="us-west-1"
```

---

## 🪜 Step 1 — Stand up the Dream Demo

```bash
git clone <repo>
cd dream-demo
cp .env.template .env          # add Stripe test keys
docker-compose up --build
docker-compose exec backend python seed_database.py
```

Open http://localhost:3000 to confirm the storefront works. This is the System Under Test for everything that follows.

---

## 🪜 Step 2 — Install the MCP Server

The `sauce-api-mcp` package ships **two** servers in one install:

- `sauce-api-mcp` — full Sauce API (account, jobs, builds, VDC, tunnels, storage)
- `sauce-api-mcp-rdc` — Real Device Cloud focused

```bash
pipx install sauce-api-mcp
which sauce-api-mcp           # → ~/.local/bin/sauce-api-mcp
which sauce-api-mcp-rdc       # → ~/.local/bin/sauce-api-mcp-rdc
```

> 💡 During the demo, run `pipx list | grep sauce` to show the audience the install is real and isolated.

---

## 🪜 Step 3 — Wire the MCP Server into Your AI Client

### Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "sauce-api-mcp-core": {
      "command": "/Users/<you>/.local/bin/sauce-api-mcp",
      "env": {
        "SAUCE_USERNAME": "${SAUCE_USERNAME}",
        "SAUCE_ACCESS_KEY": "${SAUCE_ACCESS_KEY}",
        "SAUCE_REGION": "us-west-1"
      }
    },
    "sauce-api-mcp-rdc": {
      "command": "/Users/<you>/.local/bin/sauce-api-mcp-rdc",
      "env": {
        "SAUCE_USERNAME": "${SAUCE_USERNAME}",
        "SAUCE_ACCESS_KEY": "${SAUCE_ACCESS_KEY}",
        "SAUCE_REGION": "us-west-1"
      }
    }
  }
}
```

### Gemini CLI (`~/.gemini/settings.json`)

Same `mcpServers` block as above. Restart the client after saving.

### Claude Code (project‑scoped via `.mcp.json`)

For the `claude` CLI inside this repo, drop a `.mcp.json` at the repo root with both Sauce servers. Env‑var interpolation reads from the shell that launched Claude Code, so export your creds first:

```bash
export SAUCE_USERNAME="your-username"
export SAUCE_ACCESS_KEY="your-access-key"
```

Then:

1. Create `.mcp.json` at the repo root with the same `mcpServers` block as above.
2. Restart Claude Code — on next launch it'll prompt you to approve the project‑scoped MCP servers.
3. After approval, the `mcp__sauce-api-mcp-core__*` and `mcp__sauce-api-mcp-rdc__*` tools become available.
4. Verify with `claude mcp list`.

Full config + troubleshooting lives in [`MCP_SETUP.md`](./MCP_SETUP.md).

**Verification:** open the client and ask *"What Sauce Labs tools do you have available?"* — you should see `get_recent_jobs`, `get_real_device_status`, `get_job_details`, etc.

---

## 🪜 Step 4 — Pick a Real Device with the Sauce RDC Extension

The MCP server is great for *querying* devices conversationally, but during a live demo nothing beats a glanceable visual of every real device available to your account. That's what the **Sauce RDC** VS Code extension gives you.

### Install

1. Open VS Code (or Cursor) → Extensions panel
2. Search for **"Sauce Labs"** → install **Sauce RDC** (publisher: Sauce Labs)
3. Click the Sauce icon in the Activity Bar (left rail) — a `SAUCE RDC` panel opens with three sections:

   - **REGION** — toggle between `US West`, `US East`, `EU Central` (matches `SAUCE_REGION`)
   - **DEVICES** — live roster: Pixel 9 Pro, iPhone 13, Galaxy S25, iPad Pro, etc. Green dot = available, grey = busy
   - **SESSIONS** — any sessions currently running under your account

4. Sign in: command palette → **"Sauce Labs: Sign In"** → paste `SAUCE_USERNAME` and `SAUCE_ACCESS_KEY`. The device list populates within a few seconds.

### Use it in the demo

- **Show availability live.** Right before kicking off a mobile test, expand `DEVICES` and point at the green `Google Pixel 9 Pro — Android 15.0` row. Audience sees it's a real, free device, not a screenshot.
- **Right‑click a device → Copy Device Name / Copy Capabilities.** Paste straight into your Appium `desired_capabilities` so the test you're about to run targets exactly the device you just showed.
- **Watch SESSIONS populate** the moment your `pytest` invocation starts — the row appears with a live link to the device viewer.
- **Optional flex:** click a running session to open the live device stream inside VS Code while the test executes.

> 🎯 Talking point: *"Three surfaces, one account. The RDC extension shows me what's available, the MCP tools let me ask questions about it in natural language, and Insights tells me what happened after."*

### How it complements the MCP server

| Question | Best surface |
|---|---|
| "Which Pixel devices are free **right now**?" | RDC extension (visual, live) |
| "Across the last 30 days, which device had the worst flake rate?" | MCP → Insights |
| "Pick a device and start a test" | RDC extension → copy caps → pytest |
| "Summarize failures from yesterday's run" | MCP in Claude/Gemini |

They share the exact same backend (Sauce REST API), so the device the extension shows as available is the same device MCP returns from `get_real_device_status`.

---

## 🪜 Step 5 — Run Tests Against Sauce Labs

Generate fresh data so Insights and the MCP queries have something to chew on.

**Web (VDC):**
```bash
pytest tests-e2e/test_web_checkout.py --sauce
```

**Android (RDC):**
```bash
pytest tests-e2e/test_android_app.py
```

A few of the tests intentionally fail (see [`BUGS.md`](./BUGS.md)) — that's the point. Failure is what makes Insights interesting.

---

## 🪜 Step 6 — Open Sauce AI Insights

Go to https://app.saucelabs.com → **Insights** in the left sidebar.

Demo highlights to point at:

| Tab | What to show |
|---|---|
| **Overview** | Pass/fail trend, jobs over time, platform mix |
| **Test Cases** | Click into a flaky test → duration histogram + flake score |
| **Errors** | ML‑clustered failures: "checkout button not found" grouped across 12 devices |
| **Jobs** | Filter by build name (e.g. `DreamDemo-Android-Build-1`) |

> 🎯 Talking point: *"Insights is automatic — every job that hits Sauce, web or mobile, lands here with no extra instrumentation."*

---

## 🪜 Step 7 — The Aha Moment: Drive Insights from Your AI Assistant

This is the core of the demo. With both pieces in place, your AI assistant can answer Insights‑style questions inline. Try this script:

### Prompt 1 — Account smoke test
> "Using the Sauce MCP, show my account info and current concurrency limits."

The assistant calls `get_account_info`. Confirms the connection is live.

### Prompt 2 — Recent run summary
> "What were the results of my last 10 jobs? Group by pass/fail and tell me which platforms failed most."

Assistant calls `get_recent_jobs`, summarizes — mirroring the Insights Overview.

### Prompt 3 — Drill into a failure
> "Pull the details and the Appium log for the most recent failed Android job."

Assistant chains `get_real_device_jobs` → `get_specific_real_device_job` → `get_specific_real_device_job_asset`. You now have the failure context **without ever opening a browser tab.**

### Prompt 4 — Link back to Insights
> "Give me a direct Sauce Insights URL filtered to build `DreamDemo-Android-Build-1`."

Assistant constructs the URL. Click it → land in Insights with the right filter pre‑applied.

### Prompt 5 — Triage action

### Prompt 6 — AI Test Authoring (CI-friendly)

Add CI-driven AI test authoring to your pipeline:

- Use the AI Test Authoring API to generate tests programmatically (POST /v1/ai-authoring/testcases/generate).
- Poll generation status (GET /v1/ai-authoring/testcases/generate/{taskId}) until COMPLETED, then trigger a run (POST /v1/ai-authoring/testcases/{id}/run).

Quick demo script (repo root):

```bash
# generates a test from NL prompt and triggers a Sauce run
bash scripts/sauce_ai_generate_and_run.sh "DreamDemo - checkout flow" "Add to cart, proceed to checkout, complete payment using test card" 
```

(CI integration: store SAUCE_USERNAME/SAUCE_ACCESS_KEY as pipeline secrets and call the same script during CI to generate and run tests.)
> "Based on the failure log, what part of the Dream Demo code is likely broken? Suggest a fix."

Now the assistant uses the *combination* of MCP test data + your local repo context to propose a code change. This is the "loop closes" moment.

---

## 🌟 How to Show Off the MCP Server

The "show off" beats that land best, in order:

### 1. Prove the wiring is real (10 sec)
In your AI client, ask: *"What Sauce Labs tools do you have available?"* — the assistant lists `get_recent_jobs`, `get_real_device_status`, etc. Audience sees tools materialize from the config you just showed.

### 2. Pair it with the RDC VS Code panel (visual hook)
Open the Sauce RDC sidebar so the green/grey device dots are visible while you talk to the AI. Two surfaces, same data — makes the abstract concrete.

### 3. The aha-prompt sequence
Run prompts 2 → 3 → 4 → 5 back-to-back:
- *"Summarize my last 10 jobs by pass/fail and platform."* — replaces an Insights tab
- *"Pull the Appium log for the most recent failed Android job."* — chains 3 MCP calls, no browser
- *"Give me a Sauce Insights URL filtered to build `DreamDemo-Demo-<ts>`."* — bridges back to the UI
- *"Based on that failure log, which file in this repo is likely broken? Suggest a fix."* — **this is the moment.** MCP test data + local repo context → proposed code change. The loop closes on screen.

### 4. The one-line recap
> *"Devices → Tests → Insights → MCP → AI → code change. Same account, one chat window."*

### Pre-flight, 5 min before
```bash
bash scripts/verify-mcp-setup.sh
export SAUCE_BUILD_NAME="DreamDemo-Demo-$(date +%Y%m%d-%H%M)"
pytest tests-e2e/test_android_app.py -v   # so there are fresh failures to query
```

That gives you real data with a unique build tag, so the Insights URL prompt actually narrows to something.

---

## 🎤 Suggested Demo Script (6 minutes)

| Time | What you do | What you say |
|---|---|---|
| 0:00 | Show Dream Demo at localhost:3000 | "Standard e‑commerce app, runs on web + Android." |
| 0:30 | Open the **Sauce RDC** panel in VS Code, expand `DEVICES` | "These are real devices in our cloud — green dots are free right now." |
| 1:00 | Right‑click `Google Pixel 9 Pro` → copy capabilities → paste into the test | "I pick a device the same way I'd pick a file." |
| 1:30 | Run `pytest tests-e2e/test_android_app.py` — watch `SESSIONS` light up | "Real tests, real devices, live in the editor." |
| 2:30 | Open Sauce Insights, point at Errors tab | "Every result is here, ML‑clustered, shareable." |
| 3:30 | Switch to Claude Desktop | "Now the same data, but conversational." |
| 4:00 | Run Prompts 2 → 3 → 4 above | "Triage in the same place I write code." |
| 5:00 | Run Prompt 5, accept a code edit | "MCP + Insights = test result *and* fix in one loop." |
| 5:45 | Recap diagram | "Devices → Tests → Insights → MCP → AI → code change." |

---

## 🧰 Troubleshooting Cheatsheet

| Symptom | Fix |
|---|---|
| AI client doesn't list Sauce tools | Restart client; check absolute path in config |
| `Authentication failed` | Re‑export `SAUCE_USERNAME` / `SAUCE_ACCESS_KEY`; verify with `curl -u $SAUCE_USERNAME:$SAUCE_ACCESS_KEY https://api.us-west-1.saucelabs.com/rest/v1/users/me` |
| Empty RDC results | Confirm plan includes RDC and `SAUCE_REGION` matches your account |
| Insights shows no data | Wait ~30s after job completion; verify jobs ran on Sauce, not locally |

Full guide: [`MCP_SETUP.md`](./MCP_SETUP.md) → Troubleshooting section.

---

## 💻 Copy‑Paste Terminal Commands

Everything below assumes you're at the repo root: `cd ~/Documents/GitHub/dream-demo`.

### 0. One‑time setup

```bash
# Sauce credentials (add to ~/.zshrc to persist)
export SAUCE_USERNAME="your-username"
export SAUCE_ACCESS_KEY="your-access-key"
export SAUCE_REGION="us-west-1"

# Verify creds work against the Sauce API
curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  https://api.us-west-1.saucelabs.com/rest/v1/users/$SAUCE_USERNAME | jq .

# Install pipx + the MCP servers
brew install pipx jq
pipx ensurepath
pipx install sauce-api-mcp

# Confirm the two MCP binaries are on PATH
which sauce-api-mcp
which sauce-api-mcp-rdc

# Run the project's verification script
bash scripts/verify-mcp-setup.sh
```

### 1. Stand up the Dream Demo (Step 1)

> **zsh tip:** zsh doesn't treat `#` as a comment in interactive shells by default,
> so don't paste trailing `# ...` comments into your terminal. Either drop them or run
> `setopt INTERACTIVE_COMMENTS` (add to `~/.zshrc` to persist).

```bash
cd /Users/adam.toth-fejel/Documents/GitHub/dream-demo

cp .env.template .env

open -a Docker
until docker info >/dev/null 2>&1; do echo "waiting for docker..."; sleep 2; done
echo "docker ready"
```

Then open `.env` in TextEdit:

```bash
open -e .env
```

Paste these two lines (replace with your actual keys from https://dashboard.stripe.com/test/apikeys), save, and close TextEdit:

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

Back in the terminal:

```bash
# If you previously had a half-built stack, wipe it (esp. the postgres volume):
docker-compose down -v

# Refresh the frontend's browser-compat data so webpack stops nagging
cd frontend-web && npm i baseline-browser-mapping@latest -D && npx update-browserslist-db@latest && cd ..

docker-compose up --build -d

# Wait ~20s, then sanity-check
docker-compose ps
curl -s http://localhost:8000/docs -o /dev/null -w "backend: %{http_code}\n"

# Seed runs from the host (it just hits the API), not inside the container
pip install requests
python scripts/seed_database.py

open http://localhost:3000
```

> **If the backend logs show `ModuleNotFoundError: No module named 'app'`**, your
> `docker-compose.yml` still has the old volume mount (`./backend/app:/app`). It
> should mount `./backend:/app` and run `uvicorn app.main:app`.
>
> **If `db-1 exited with code 1` with "data directory was initialized by
> PostgreSQL version 15"**, you have a stale volume from a previous run —
> `docker-compose down -v` clears it.

#### Recover a broken stack (copy‑paste recipe)

If your current stack is half‑built or wedged, run these in order to recover:

```bash
cd /Users/adam.toth-fejel/Documents/GitHub/dream-demo
docker-compose down -v
cd frontend-web && npm i baseline-browser-mapping@latest -D && npx update-browserslist-db@latest && cd ..
docker-compose up --build -d
sleep 20
docker-compose ps
curl -s http://localhost:8000/docs -o /dev/null -w "backend: %{http_code}\n"
pip install requests
python scripts/seed_database.py
open http://localhost:3000
```

### 2. Install the Sauce RDC VS Code extension (Step 4)

```bash
# VS Code
code --install-extension saucelabs.sauce-rdc

# Cursor (uses the same marketplace)
cursor --install-extension saucelabs.sauce-rdc

# Open the project so the extension activates
code .
```

Then in the editor: command palette → **"Sauce Labs: Sign In"** → paste username + access key.

### 3. Sanity‑check the MCP servers without an AI client

```bash
# These should print "INFO: SauceAPI client initialized…" then exit / hang
sauce-api-mcp --help 2>&1 | head -5
sauce-api-mcp-rdc --help 2>&1 | head -5

# Optional: hit the same endpoints MCP uses, to prove data is there
curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/v1/rdc/devices" | jq '.[0:5]'

curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/rest/v1/$SAUCE_USERNAME/jobs?limit=5" | jq '.[] | {id, name, passed}'
```

### 4. Restart your AI client to pick up the MCP config

```bash
# Claude Desktop
osascript -e 'quit app "Claude"' ; sleep 2 ; open -a "Claude"

# Gemini CLI — just relaunch your shell session
exec $SHELL -l
```

### 5. Run tests against Sauce Labs (Step 5)

```bash
# Python test deps (one‑time)
python3 -m venv .venv && source .venv/bin/activate
pip install -r tests-e2e/requirements.txt

# Tag this run so it's easy to filter in Insights
export SAUCE_BUILD_NAME="DreamDemo-Demo-$(date +%Y%m%d-%H%M)"
echo "Build: $SAUCE_BUILD_NAME"

# Web tests (Chrome + Firefox on Windows 10 via VDC)
pytest tests-e2e/test_web_app.py -v

# Android tests on RDC — requires the app uploaded to Sauce storage
# Upload the APK once:
curl -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  -X POST "https://api.us-west-1.saucelabs.com/v1/storage/upload" \
  -F "payload=@android-app/app/build/outputs/apk/debug/app-debug.apk" \
  -F "name=flowershop.apk" | jq '.item.id'

# Then run the RDC tests
export SAUCE_APP_ID="storage:filename=flowershop.apk"

# (Optional) Target the exact device you picked from the Sauce RDC VS Code
# extension. If unset, the fixture runs against its default device matrix.
export SAUCE_DEVICE_NAME="Google Pixel 9 Pro"
export SAUCE_PLATFORM_VERSION="15"

pytest tests-e2e/test_android_app.py -v
```

Watch the **SESSIONS** section of the Sauce RDC panel light up while these run.

### 6. Open Sauce AI Insights (Step 6)

```bash
# Jump straight to Insights filtered by the build you just ran
open "https://app.saucelabs.com/insights?buildName=$SAUCE_BUILD_NAME"
```

### 7. Quick MCP queries to paste into Claude / Gemini (Step 7)

These aren't shell commands — paste them into your AI client's chat after the run:

```text
1. Show my Sauce account info and concurrency limits.
2. Summarize my last 10 jobs by pass/fail and platform.
3. Pull the Appium log for the most recent failed Android job.
4. Give me a Sauce Insights URL filtered to build DreamDemo-Demo-<timestamp>.
5. Based on that failure log, which file in this repo is likely broken? Suggest a fix.
```

### 8. Teardown

```bash
docker-compose down       # stop services, keep DB
docker-compose down -v    # … also wipe the database
deactivate 2>/dev/null    # exit the python venv
```

---

## 📚 References

- Sauce MCP server: https://github.com/saucelabs/sauce-api-mcp
- Sauce Insights docs: https://docs.saucelabs.com/insights/
- Model Context Protocol: https://modelcontextprotocol.io
- Project setup: [`README.md`](./README.md), [`MCP_SETUP.md`](./MCP_SETUP.md)
- Intentional bugs to demo against: [`BUGS.md`](./BUGS.md)
