# RDC API Plugin — 60-Second Demo Script

Quick showcase of the `sauce-api-mcp-rdc` MCP plugin for Sauce Labs Real Device Cloud.

---

## Pre-Demo (5 sec)

Ensure Claude Desktop (or Gemini CLI) is open with the RDC server connected.

```
Status bar should show: "Sauce API RDC" as an active MCP server.
```

---

## Demo Flow

### 0:00–0:10 — The Hook

**Say:** *"When you're about to run a mobile test, the first question is always: what devices are actually available right now?"*

**Type:**
```
What Android devices are available in us-west-1?
```

**Screen shows:** Claude calls `get_real_device_status` and returns a live list of real Android devices (Pixel 8, Galaxy S24, etc.) with OS versions and availability.

---

### 0:10–0:25 — Deep Dive

**Say:** *"I can drill down instantly. Show me the details for the Pixel 8."*

**Type:**
```
Show me the details for Pixel 8
```

**Screen shows:** Device resolution, OS version, API level, whether it's currently free or in use.

---

### 0:25–0:40 — Real Jobs, Real Data

**Say:** *"I just ran an Appium test. Let me check how it did — without opening a browser."*

**Type:**
```
Show my recent RDC jobs
```

**Screen shows:** `get_real_device_jobs` returns the latest real-device test runs with pass/fail status, duration, and device used.

---

### 0:40–0:55 — Asset Retrieval

**Say:** *"That one failed. I need the logs — right here in the chat."*

**Type:**
```
Get the logs for my most recent failed RDC job
```

**Screen shows:** Claude calls `get_specific_real_device_job_asset`, returns a download link to the device logs and session video.

---

### 0:55–1:00 — The Close

**Say:** *"No dashboard clicks. No context switching. Just ask."*

**Screen shows:** All four answers still visible in the chat thread.

---

## Key Talking Points

| Beat | Point |
|------|-------|
| **Hook** | Live device catalog eliminates "guess and check" before scheduling tests |
| **Drill-down** | Resolution, OS, API level — all programmatically accessible |
| **Jobs** | RDC test results surfaced inside the AI assistant, not buried in a web UI |
| **Assets** | Logs and videos fetched via API — shareable links generated instantly |
| **Close** | Natural language replaces 4+ dashboard navigations |

---

## On-Screen Checklist

- [ ] Claude Desktop window visible
- [ ] `.mcp.json` shows `sauce-api-mcp-rdc` configured (optional quick flash)
- [ ] Each query typed live (don't paste all at once)
- [ ] Tool call badge visible ("Sauce API RDC" icon in Claude)
- [ ] Responses show real data, not mock text

---

## Fallback Prompts

If no recent jobs exist in the account:

```
List available iPhone models
```

```
What real devices are currently busy?
```

```
Show me RDC job history from the last 7 days
```

---

## Extended Demo: MCP + saucectl End-to-End

Show how device discovery flows directly into test execution.

### Script

**Say:** *"I found a device. Now I want to run tests on it — without touching the dashboard."*

**Switch to terminal. Run:**
```bash
./scripts/demo_mcp_saucectl.sh
```

**Terminal shows:**
1. **Device Discovery** — Python script queries RDC API and lists available Android/iOS devices
2. **saucectl run** — Playwright web tests uploaded and executed on Sauce Labs VDC (Windows 11 + Chromium/Firefox/WebKit)
3. **pytest run** — Appium mobile tests executed on the chosen real device (e.g., Google Pixel 8)
4. **Job Analysis** — Recent RDC jobs fetched and displayed with pass/fail status

**Say:** *"That single script did four things: discovered devices, ran web tests via saucectl, ran mobile tests via pytest, and pulled the results back — all from the terminal."*

### Files Used

| File | Purpose |
|------|---------|
| `scripts/demo_mcp_device_discovery.py` | Standalone MCP-style RDC device query |
| `scripts/demo_mcp_saucectl.sh` | Orchestrates full discovery → run → analysis flow |
| `.sauce/config.yml` | saucectl config for Playwright web tests |
| `tests-playwright/flower-shop.spec.js` | Playwright e2e tests for Flower Shop web app |
| `tests-e2e/test_android_app.py` | Appium tests for mobile (run via pytest, not saucectl) |

### Key Talking Point

`saucectl` runs the tests you specify, but it cannot browse the live RDC catalog. The MCP plugin (or the standalone discovery script) fills that gap: **discover** with MCP, **execute** with saucectl, **analyze** with MCP again.

---

## One-Liner Summary

> The RDC API plugin turns Sauce Labs Real Device Cloud into a conversational interface — query devices, jobs, and test assets without leaving your AI assistant.
