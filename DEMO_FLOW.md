# Demo Flow

Two flows on one repo. Branches conflict on port 8000 — `docker-compose down` before switching.

## Setup

```bash
export SAUCE_USERNAME="your-username"
export SAUCE_ACCESS_KEY="your-access-key"
export SAUCE_REGION="us-west-1"
```

## Flow 1: AI Test Authoring (Web) — `sprint-3`

```bash
git checkout sprint-3
docker-compose up -d backend db frontend
sleep 10
python3 scripts/seed_database.py
curl -s -X POST http://localhost:8000/users/ -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

Expose localhost via Serveo (run in separate terminals):
```bash
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R 80:localhost:3000 serveo.net
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R 80:localhost:8000 serveo.net
```

Rebuild frontend with the backend tunnel URL, then run:
```bash
scripts/sauce_ai_web.sh "DreamDemo Web - Login and Browse" \
  "Login with test@example.com and password testpassword123, verify Our Products section" \
  "DreamDemo-AI-$(date +%s)"
```

## Flow 2: Mobile Appium (RDC) — `sprint-2-mobile`

```bash
docker-compose down -v  # critical
git checkout sprint-2-mobile
backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3

export SAUCE_TUNNEL_NAME="demo-tunnel-$(date +%s)"
export SAUCE_APP_ID="storage:94eb7fcd-c35f-47d0-814d-627ce0e35aed"
sc run -u "$SAUCE_USERNAME" -k "$SAUCE_ACCESS_KEY" -r us-west-1 \
  -i "$SAUCE_TUNNEL_NAME" --proxy-localhost allow --log-file sc.log &
sleep 90  # 30s for "up" + 60s propagation

pytest tests-e2e/test_two_specific.py \
  -k "test_successful_login or test_add_product_to_cart" -v
```

## Gotchas

- **Port 8000 conflict:** `docker-compose down -v` before `git checkout sprint-2-mobile`
- **Tunnel propagation:** `sleep 60` after Sauce Connect says "up" before running tests
- **Android popups:** `autoGrantPermissions: True` in `conftest_android.py`
- **Chrome popups:** `--disable-notifications` in `goog:chromeOptions` for AI tests
- **Mark RDC passed:** `driver.execute_script("sauce:job-result=passed")` in fixture teardown
