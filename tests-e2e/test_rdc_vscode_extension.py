"""
RDC VS Code Extension Test — Flower Shop E2E Flow

Purpose: A self-contained test designed to run inside the Sauce Labs
Real Device Cloud (RDC) VS Code extension. No external conftest imports.

VS Code Extension Workflow:
    1. Open Command Palette → "Sauce Labs: Select Device"
    2. Pick an Android device (e.g., Google Pixel 8)
    3. The extension sets SAUCE_DEVICE_NAME / SAUCE_PLATFORM_VERSION
    4. Right-click this file → "Run Test on Sauce Labs"

Manual run (requires env vars):
    export SAUCE_USERNAME="your-username"
    export SAUCE_ACCESS_KEY="your-access-key"
    export SAUCE_DEVICE_NAME="Google Pixel 8"   # optional, uses default if unset
    export SAUCE_PLATFORM_VERSION="14"          # optional, uses default if unset
    export SAUCE_APP_ID="storage:filename=flowershop.apk"
    pytest test_rdc_vscode_extension.py -v

Test Flow:
    1. Launch app on real device
    2. Log in with test credentials
    3. Verify product catalog loads
    4. Add a product to cart
    5. Open cart and verify item is present
"""

import os
import time
import pytest
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ---------------------------------------------------------------------------
# Configuration — the extension sets SAUCE_DEVICE_NAME / SAUCE_PLATFORM_VERSION
# ---------------------------------------------------------------------------
SAUCE_USERNAME = os.getenv("SAUCE_USERNAME")
SAUCE_ACCESS_KEY = os.getenv("SAUCE_ACCESS_KEY")
SAUCE_URL = (
    f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}"
    f"@ondemand.us-west-1.saucelabs.com:443/wd/hub"
)

DEFAULT_DEVICE = os.getenv("SAUCE_DEVICE_NAME", "Google Pixel 8")
DEFAULT_PLATFORM = os.getenv("SAUCE_PLATFORM_VERSION", "14")
SAUCE_APP_ID = os.getenv("SAUCE_APP_ID", "storage:filename=flowershop.apk")


# ---------------------------------------------------------------------------
# Pytest hook to capture pass/fail status for Sauce Labs reporting
# ---------------------------------------------------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ---------------------------------------------------------------------------
# Fixture: launch app on the device chosen in the VS Code extension
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def driver(request):
    if not SAUCE_USERNAME or not SAUCE_ACCESS_KEY:
        pytest.skip("SAUCE_USERNAME and SAUCE_ACCESS_KEY must be set")

    test_name = request.node.name

    options = UiAutomator2Options()
    options.app = SAUCE_APP_ID
    options.platform_name = "Android"
    options.device_name = DEFAULT_DEVICE
    options.platform_version = DEFAULT_PLATFORM
    options.automation_name = "UiAutomator2"
    options.set_capability("autoGrantPermissions", True)

    sauce_options = {
        "username": SAUCE_USERNAME,
        "accessKey": SAUCE_ACCESS_KEY,
        "build": os.getenv("SAUCE_BUILD_NAME", "FlowerShop-RDC-VSCode"),
        "name": test_name,
        "deviceOrientation": "PORTRAIT",
        "appiumVersion": "appium2-20250901",
    }

    # Attach Sauce Connect tunnel if one is active
    sc_tunnel = os.getenv("SAUCE_TUNNEL_NAME") or os.getenv("SAUCE_SC_TUNNEL")
    if sc_tunnel:
        sauce_options["tunnelIdentifier"] = sc_tunnel
        sauce_options["scTunnelName"] = sc_tunnel

    options.set_capability("sauce:options", sauce_options)

    driver = webdriver.Remote(command_executor=SAUCE_URL, options=options)
    yield driver

    # Report result back to Sauce Labs (RDC REST API)
    try:
        sauce_result = "passed" if getattr(request.node, "rep_call", None) and request.node.rep_call.passed else "failed"

        # VDC marker (best-effort)
        try:
            driver.execute_script(f"sauce:job-result={sauce_result}")
        except Exception:
            pass

        # RDC marker (reliable on real devices)
        try:
            resp = requests.put(
                f"https://api.us-west-1.saucelabs.com/v1/rdc/jobs/{driver.session_id}",
                auth=(SAUCE_USERNAME, SAUCE_ACCESS_KEY),
                json={"passed": sauce_result == "passed"},
                timeout=5,
            )
            print(f"[Sauce RDC] Job {driver.session_id} marked as {sauce_result}: {resp.status_code}")
        except Exception as e:
            print(f"[Sauce RDC] Failed to update job {driver.session_id}: {e}")
    except Exception:
        pass

    driver.quit()


# ---------------------------------------------------------------------------
# Helper: robust login with fallbacks and debug artifact capture
# ---------------------------------------------------------------------------
def _do_login(drv, email="test@example.com", password="testpassword123"):
    """
    Perform login on the Flower Shop auth screen.
    Returns True if login succeeded, False otherwise.
    Saves screenshot + page source on failure.
    """
    wait = WebDriverWait(drv, 15)

    # Wait for auth screen
    wait.until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Flower Shop')]"))
    )

    # Locate input fields
    inputs = drv.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
    if len(inputs) >= 2:
        email_el, password_el = inputs[0], inputs[1]
    else:
        email_el = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[1]")))
        password_el = drv.find_element(AppiumBy.XPATH, "//android.widget.EditText[2]")

    # Fill email
    for action in [lambda: email_el.clear() or email_el.set_value(email), lambda: email_el.send_keys(email)]:
        try:
            action()
            break
        except Exception:
            continue

    # Fill password
    for action in [lambda: password_el.clear() or password_el.set_value(password), lambda: password_el.send_keys(password)]:
        try:
            action()
            break
        except Exception:
            continue

    # Dismiss keyboard
    try:
        drv.hide_keyboard()
    except Exception:
        pass

    # Find and click login button
    login_btn = None
    try:
        login_btn = WebDriverWait(drv, 5).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text,'Login')]/ancestor::*[@clickable='true'][1]")
            )
        )
    except Exception:
        try:
            login_btn = drv.find_element(AppiumBy.XPATH, "//*[@text='Login']")
        except Exception:
            pass

    if not login_btn:
        _capture_debug(drv, "login_no_button")
        return False

    # Click with retry + coordinate fallback
    for attempt in range(3):
        try:
            login_btn.click()
        except Exception:
            try:
                loc = login_btn.location
                size = login_btn.size
                x = loc["x"] + size["width"] // 2
                y = loc["y"] + size["height"] // 2
                drv.execute_script("mobile: clickGesture", {"x": x, "y": y})
            except Exception:
                pass

        time.sleep(1)
        try:
            home = WebDriverWait(drv, 3).until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]")
                )
            )
            if home:
                return True
        except Exception:
            pass

    # Fallback locators
    alt_locators = [
        (AppiumBy.ACCESSIBILITY_ID, "Login"),
        (AppiumBy.XPATH, "//*[contains(@resource-id,'login')]"),
    ]
    for by, val in alt_locators:
        try:
            alt = drv.find_element(by, val)
            try:
                alt.click()
            except Exception:
                loc = alt.location
                size = alt.size
                drv.execute_script(
                    "mobile: clickGesture",
                    {"x": loc["x"] + size["width"] // 2, "y": loc["y"] + size["height"] // 2},
                )
            time.sleep(1)
            try:
                WebDriverWait(drv, 3).until(
                    EC.presence_of_element_located(
                        (AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]")
                    )
                )
                return True
            except Exception:
                pass
        except Exception:
            continue

    _capture_debug(drv, "login_failed")
    return False


def _capture_debug(drv, prefix):
    """Save screenshot and page source to /tmp for troubleshooting."""
    try:
        ts = int(time.time())
        png = f"/tmp/{prefix}_{ts}.png"
        xml = f"/tmp/{prefix}_{ts}.xml"
        try:
            drv.save_screenshot(png)
        except Exception:
            pass
        try:
            with open(xml, "w", encoding="utf-8") as f:
                f.write(drv.page_source)
        except Exception:
            pass
        print(f"DEBUG: saved {png} and {xml}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestFlowerShopRDC:
    """End-to-end flow: login → browse → cart — optimized for RDC VS Code extension."""

    # -----------------------------------------------------------------------
    # Test 1: Login
    # -----------------------------------------------------------------------
    def test_login_success(self, driver):
        """User can log in and land on the home screen."""
        assert _do_login(driver), "Login failed — see debug artifacts in /tmp"

        wait = WebDriverWait(driver, 10)
        home = wait.until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]")
            )
        )
        assert home.is_displayed(), "Home screen not visible after login"

    # -----------------------------------------------------------------------
    # Test 2: Browse Products
    # -----------------------------------------------------------------------
    def test_products_loaded(self, driver):
        """Product catalog displays items with 'Add to Cart' buttons."""
        assert _do_login(driver), "Login failed"

        wait = WebDriverWait(driver, 10)
        add_buttons = wait.until(
            EC.presence_of_all_elements_located(
                (AppiumBy.XPATH, "//*[contains(@text, 'Add to Cart')]")
            )
        )
        assert len(add_buttons) > 0, "No products with 'Add to Cart' found"

    # -----------------------------------------------------------------------
    # Test 3: Add to Cart
    # -----------------------------------------------------------------------
    def test_add_to_cart(self, driver):
        """User can add a product to the shopping cart."""
        assert _do_login(driver), "Login failed"

        wait = WebDriverWait(driver, 10)

        # Tap first "Add to Cart" button
        add_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "(//*[contains(@text, 'Add to Cart')])[1]"))
        )
        add_btn.click()
        time.sleep(1)  # let UI update

        # Verify badge appears (look for "1" near cart icon)
        badge = driver.find_elements(AppiumBy.XPATH, "//*[@text='1']")
        assert len(badge) > 0, "Cart badge did not appear after adding item"

    # -----------------------------------------------------------------------
    # Test 4: Cart contains item
    # -----------------------------------------------------------------------
    def test_cart_has_item(self, driver):
        """Cart screen shows the added item with price details."""
        assert _do_login(driver), "Login failed"

        wait = WebDriverWait(driver, 10)

        # Add item
        add_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "(//*[contains(@text, 'Add to Cart')])[1]"))
        )
        add_btn.click()
        time.sleep(0.5)

        # Open cart via accessibility ID
        cart_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Cart"))
        )
        cart_btn.click()
        time.sleep(0.5)

        # Verify cart content (price or total text)
        cart_items = driver.find_elements(
            AppiumBy.XPATH,
            "//*[contains(@text, '$') or contains(@text, 'Total')]",
        )
        assert len(cart_items) > 0, "Cart screen does not show price/total content"
