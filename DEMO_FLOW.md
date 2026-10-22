# Adam's Demo — Sauce AI Testing & Error Monitoring

End-to-end Sauce Labs demo: visual regression → real-device testing (RDC plugin) → error
monitoring (Sauce Backtrace) → fix → test authoring → AI insights.
Always begin with `docker-compose down -v` before switching branches to prevent port conflicts.

## Setup

```bash
export SAUCE_USERNAME="your-username"
export SAUCE_ACCESS_KEY="your-access-key"
export SAUCE_REGION="us-west-1"
```

The RDC steps use the `sauce-api-mcp-rdc` MCP server (configured in `.mcp.json`) and the
Sauce Labs **RDC plugin** in VS Code.

## Sauce Ecosystem Demo

Complete flow leveraging Sauce Visual → RDC Plugin → Error Detection → Sauce Backtrace → Fix → Sauce Test Authoring → Sauce AI Insights.

1. **Sauce Visual** - Visual regression testing to establish baseline
2. **RDC Plugin** - Real device testing in VSCode
3. **Error Firing** - App error occurs during execution
4. **Sauce Backtrace** - Automatically detected via Slack integration
5. **Backtrace Analysis** - Identify root cause using stack traces
6. **Fix** - Apply fix to the codebase
7. **Sauce Test Authoring** - Create regression test to catch the error if reintroduced
8. **Sauce AI Insights** - Verify fix and gain AI-powered test insights

### Step 2 in detail — RDC Plugin: load the app and click around

The RDC plugin turns a real device in Sauce's data centers into a remote, scriptable
session you can drive from VS Code or from chat. This is the "click around on buttons"
part of the demo, made explicit.

#### A. Select a device

**In VS Code (RDC plugin):**

1. Open the Command Palette (`⌘⇧P`) → **Sauce Labs: Select Device**.
2. Pick an Android device (e.g. **Samsung Galaxy A51** or **Google Pixel 8**).
   The plugin exports `SAUCE_DEVICE_NAME` / `SAUCE_PLATFORM_VERSION` for the run.
3. Right-click `tests-e2e/test_rdc_vscode_extension.py` → **Run Test on Sauce Labs**.

**Or from chat** (the assistant calls the `sauce-api-mcp-rdc` tools):

```
List available Android devices
```

```
Allocate a Samsung Galaxy A51 and wait until it is ACTIVE
```

Under the hood that is `list_device_status` → `allocate_device_and_create_session`,
then `get_session_details` polled until the session state is `ACTIVE`.

#### B. Load the app onto the device

Install the Flower Shop APK from Sauce Storage and launch it:

```
Install storage:filename=flowershop.apk on my active device and launch it
```

`install_app_from_storage` installs the app and starts its main activity. Wait for the
**Flower Shop** login screen to render before tapping anything.

> Known quirk: `install_app_from_storage` with `features={"networkCapture": true}` fails on
> this MCP build (the `features` object is serialized to a string). Install without `features`.

#### C. Click around — the happy path

Drive the UI by asking for the element you want tapped. At each step the assistant locates
the element by its visible text / accessibility id and taps its centre
(`mobile: clickGesture` under the hood).

1. **Log in** — fill the two `android.widget.EditText` fields, then tap **Login**:
   ```
   Type "test@example.com" into the first field, "testpassword123" into the second, then tap "Login"
   ```
2. **Browse** — confirm the catalog rendered and add an item:
   ```
   Tap the first "Add to Cart" button
   ```
3. **Open the cart** — tap the cart icon (accessibility id `Cart`):
   ```
   Tap the Cart icon
   ```
4. **Verify** — the cart now shows the item and a total:
   ```
   What is in my cart?
   ```

The concrete locators behind those taps (same ones `test_rdc_vscode_extension.py` uses):

| Element | Locator | Action |
|---|---|---|
| Email field | `android.widget.EditText[1]` | `set_value("test@example.com")` |
| Password field | `android.widget.EditText[2]` | `set_value("testpassword123")` |
| **Login** | `//*[contains(@text,'Login')]/ancestor::*[@clickable='true'][1]` | tap (retry + coordinate fallback) |
| **Add to Cart** | `(//*[contains(@text,'Add to Cart')])[1]` | tap |
| Cart | accessibility id `Cart` | tap |
| Cart badge | `//*[@text='1']` | assert it appears |

#### D. Or run the whole click-through as a test

```bash
export SAUCE_DEVICE_NAME="Google Pixel 8"
export SAUCE_PLATFORM_VERSION="14"
export SAUCE_APP_ID="storage:filename=flowershop.apk"
pytest tests-e2e/test_rdc_vscode_extension.py -v
```

Then release the device:

```
Close my active session
```

(`close_device_session`; the device returns to the pool clean for the next run.)

### Running the RDC Flow

```bash
docker-compose down -v  # Required: clean slate before mobile flow
git checkout sprint-2-mobile

# Start backend
backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3

# Start Sauce Connect tunnel
export SAUCE_TUNNEL_NAME="demo-tunnel-$(date +%s)"
export SAUCE_APP_ID="storage:94eb7fcd-c35f-47d0-814d-627ce0e35aed"
sc run -u "$SAUCE_USERNAME" -k "$SAUCE_ACCESS_KEY" -r us-west-1 \
  -i "$SAUCE_TUNNEL_NAME" --proxy-localhost allow --log-file sc.log &
sleep 90  # 30s for tunnel up + 60s propagation

# Run tests (will trigger error path, trigger Backtrace, complete after fix is applied)
pytest tests-e2e/test_two_specific.py \
  -k "test_successful_login or test_add_product_to_cart" -v
```

### AI Test Authoring Subflow (Web)

```bash
git checkout sprint-3
docker-compose up -d backend db frontend
sleep 10
python3 scripts/seed_database.py
curl -s -X POST http://localhost:8000/users/ -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'

export SAUCE_TUNNEL_NAME="web-ai-tunnel-$(date +%s)"
sc run -u "$SAUCE_USERNAME" -k "$SAUCE_ACCESS_KEY" -r us-west-1 \
  -i "$SAUCE_TUNNEL_NAME" --proxy-localhost allow &
sleep 90

export SAUCE_TUNNEL_NAME
scripts/sauce_ai_web.sh "DreamDemo Web - Login and Browse" \
  "Login with test@example.com and password testpassword123, verify Our Products section" \
  "DreamDemo-AI-$(date +%s)"
```

## Gotchas

- **Port 8000 conflict:** `docker-compose down -v` before `git checkout sprint-2-mobile`
- **Tunnel propagation:** `sleep 60` after Sauce Connect says "up" before running tests
- **Sauce Connect > Serveo:** No security warning page, no Chrome permission popups
- **Android popups:** `autoGrantPermissions: True` in `conftest_android.py`
- **Mark RDC passed:** `driver.execute_script("sauce:job-result=passed")` in fixture teardown
