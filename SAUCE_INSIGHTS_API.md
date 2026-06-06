# Sauce AI Insights API — Reference

What we learned from `NetworkCalls/TestInsightsApi.har` and the working REST API alternative.

---

## 1. What the HAR captured

The HAR file shows a **WebSocket** conversation with the Sauce Labs AI Assistant:

```
GET wss://api.us-west-1.saucelabs.com/ai-assistant-gateway/v1/chat/ws/{uuid}
```

The user asked:
> "What is the Error Rate trend over the past seven days and show me the top five errors by count."

The server streamed back 4 messages:
1. `PROCESSING` — intro text widget
2. `PROCESSING` — line chart with daily error counts
3. `PROCESSING` — text + markdown table of top errors
4. `DONE` — stream complete

---

## 2. The auth problem

**Basic Auth (API keys) works for REST APIs, but NOT for the AI Assistant WebSocket.**

| Endpoint | Auth | Result |
|----------|------|--------|
| `wss://.../ai-assistant-gateway/v1/chat/ws` | Basic Auth | **HTTP 403 Forbidden** |
| `https://.../rest/v1/{user}/jobs` | Basic Auth | ✅ 200 OK |
| `https://.../v1/ai-authoring/testcases` | Basic Auth | ✅ 200 OK |

The AI Assistant WebSocket requires a **browser session cookie** (SSO login). It is an internal web UI feature, not a public programmatic API.

**Attempted workarounds:**
- Cookie scraping from `app.saucelabs.com` → blocked by nginx/SSO
- Direct form login → 403 Forbidden

**Conclusion:** The WebSocket is not accessible via API keys.

---

## 3. The REST API alternative (works with API keys)

The AI Assistant is just a chat UI over these public REST endpoints:

### Get error trends (daily histogram)
```bash
curl -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/v2/insights/vdc/errors/trends?org_id=ORG_ID&start=2026-05-01T00:00:00Z&end=2026-06-01T00:00:00Z&interval=1d"
```

### Get top errors by count
```bash
curl -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/v2/insights/vdc/errors?org_id=ORG_ID&start=2026-05-01T00:00:00Z&end=2026-06-01T00:00:00Z&limit=5"
```

### Get test listing
```bash
curl -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/v1/analytics/tests?time_range=30d&size=10"
```

### Get test trends
```bash
curl -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" \
  "https://api.us-west-1.saucelabs.com/v1/analytics/trends/tests?time_range=7d&interval=1d&scope=me"
```

---

## 4. Scripts created

### Mock server (for understanding the protocol)
```bash
# Terminal 1 — start the mock WebSocket server
python3 scripts/mock_ai_insights_server.py

# Terminal 2 — test the client
python3 scripts/test_ai_insights_client.py --host ws://localhost:8765 --timeout 10
```

Replays the exact 4-message stream from the HAR file.

### Test client (WebSocket)
```bash
# Works against the mock server
python3 scripts/test_ai_insights_client.py --host ws://localhost:8765 --timeout 10

# Does NOT work against the real API (HTTP 403)
python3 scripts/test_ai_insights_client.py --host wss://api.us-west-1.saucelabs.com --timeout 60
```

### Real Insights report (REST API)
```bash
export SAUCE_USERNAME="..."
export SAUCE_ACCESS_KEY="..."

# 7-day report
python3 scripts/sauce_insights_report.py

# 30-day report
python3 scripts/sauce_insights_report.py 30

# 90-day report
python3 scripts/sauce_insights_report.py 90
```

Fetches **real data** from Sauce Labs and prints:
- Error trend histogram
- Top errors by count
- Test status breakdown (passed/failed/errored/complete)
- Pass/fail/error rates
- JSON dump saved to `sauce-insights-{days}d.json`

---

## 5. Sample output (real data)

```
Sauce Labs Insights Report
Account: oauth-adam.toth-fejel-09cd4
Errors: Last 30 days  |  Tests: Last 30 days
Generated: 2026-06-03T07:48:52Z

SUMMARY
  Total Tests:         53
  Total Errors:        9
  Peak Error Day:      2026-05-17 (9 errors)
  Pass Rate:           47.2%
  Error Rate:          0.0%
  Fail Rate:           11.3%

ERROR TREND (daily)
  2026-05-15  |░░░░░░░░░░░░░░░░░░░░|  0
  2026-05-16  |░░░░░░░░░░░░░░░░░░░░|  0
  2026-05-17  |████████████████████|  9
  2026-05-18  |░░░░░░░░░░░░░░░░░░░░|  0

TOP ERRORS
  6  Misconfigured -- No active tunnel found for provider
  1  Tunnels API error: status_code=404
  1  Tunnels API error: status_code=404
  1  Test did not see a new command for 600 seconds. Timing out.

TEST STATUS BREAKDOWN
  passed   25
  failed   6
  error    9
  complete 13
```

**Insight:** On May 17th, 6 out of 9 errors were "no active tunnel found" — the Sauce Connect tunnel wasn't running when AI tests tried to start.

---

## 6. Dependencies

```
websockets   # for test client
fastapi      # for mock server
uvicorn      # for mock server
requests     # for REST API calls (already in requirements.txt)
```

Already added to `backend/requirements.txt`.

---

## 7. File list

| File | Purpose |
|------|---------|
| `scripts/mock_ai_insights_server.py` | WebSocket mock server |
| `scripts/test_ai_insights_client.py` | WebSocket test client |
| `scripts/sauce_insights_client.py` | Minimal REST API client |
| `scripts/sauce_insights_report.py` | Full weekly report generator |
| `NetworkCalls/TestInsightsApi.har` | Original HAR capture |
| `NetworkCalls/extracted_ai_insights.json` | Parsed HAR data |
| `scripts/try_cookie_auth.py` | Failed cookie auth attempt (for reference) |

---

## 8. Key takeaway

The Sauce AI Assistant WebSocket is **not a public API**. Use the **Insights REST APIs** for programmatic access to the same data.

- `/v2/insights/{vdc,rdc}/errors/trends` — error counts over time
- `/v2/insights/{vdc,rdc}/errors` — top errors by count
- `/v1/analytics/tests` — individual test results
- `/v1/analytics/trends/tests` — aggregated test trends
- `/v1/analytics/trends/builds_tests` — build-level trends

All endpoints accept `org_id`, `start`/`end` dates or `time_range`, and `scope` (me/organization/single).
