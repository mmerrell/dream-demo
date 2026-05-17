import pytest
import time
import requests
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

# Copy the android_driver fixture from conftest_android.py
SAUCE_USERNAME = os.getenv("SAUCE_USERNAME")
SAUCE_ACCESS_KEY = os.getenv("SAUCE_ACCESS_KEY")

# Sauce Labs URL
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.us-west-1.saucelabs.com:443/wd/hub"

# Default RDC device when none is specified via env or fixture parameter.
DEFAULT_SAUCE_DEVICE_NAME = os.getenv("SAUCE_DEVICE_NAME", "Google Pixel 8")
DEFAULT_SAUCE_PLATFORM_VERSION = os.getenv("SAUCE_PLATFORM_VERSION", "14")

from appium.options.android import UiAutomator2Options

def get_sauce_options(test_name: str, device_name: str) -> UiAutomator2Options:
    """Configure options for Sauce Labs Real Device Cloud."""
    options = UiAutomator2Options()
    
    # App can be uploaded to Sauce Labs storage or referenced by URL
    options.app = os.getenv("SAUCE_APP_ID", "storage:filename=flowershop.apk")
    
    # Device capabilities
    options.platform_name = "Android"
    options.device_name = device_name
    options.automation_name = "UiAutomator2"
    
    # Sauce Labs specific options
    sauce_options = {
        "username": SAUCE_USERNAME,
        "accessKey": SAUCE_ACCESS_KEY,
        "build": os.getenv("SAUCE_BUILD_NAME", "FlowerShop-Android-Build-1"),
        "name": test_name,
        "deviceOrientation": "PORTRAIT",
        "appiumVersion": "appium2-20250901",
    }
    
    # If a Sauce Connect tunnel name is provided, attach it so the device can reach localhost services
    sc_tunnel = os.getenv("SAUCE_TUNNEL_NAME") or os.getenv("SAUCE_SC_TUNNEL")
    if sc_tunnel:
        # Different fields used in various Sauce tooling; set both common keys
        sauce_options["tunnelIdentifier"] = sc_tunnel
        sauce_options["scTunnelName"] = sc_tunnel

    options.set_capability("sauce:options", sauce_options)
    
    return options

@pytest.fixture
def android_driver(request):
    """
    Smart fixture that uses Sauce Labs if credentials are available,
    otherwise falls back to local Appium.
    """
    test_name = request.node.name
    
    if SAUCE_USERNAME and SAUCE_ACCESS_KEY:
        # Use Sauce Labs — honor SAUCE_DEVICE_NAME / SAUCE_PLATFORM_VERSION
        # so a single command can target whatever device you picked from the
        # Sauce RDC VS Code extension.
        options = get_sauce_options(test_name, DEFAULT_SAUCE_DEVICE_NAME)
        options.platform_version = DEFAULT_SAUCE_PLATFORM_VERSION
        
        driver = webdriver.Remote(
            command_executor=SAUCE_URL,
            options=options
        )
        
        yield driver
        
        # Report result to Sauce Labs
        try:
            sauce_result = "passed" if request.node.rep_call.passed else "failed"
            driver.execute_script(f"sauce:job-result={sauce_result}")
        except:
            pass
        driver.quit()
    else:
        # Use local Appium
        app_path = os.getenv("ANDROID_APP_PATH")
        options = get_local_options(app_path)
        
        driver = webdriver.Remote(
            command_executor=LOCAL_APPIUM_URL,
            options=options
        )
        
        yield driver
        driver.quit()

def get_local_options(app_path: str = None) -> UiAutomator2Options:
    """Configure options for local Appium testing."""
    options = UiAutomator2Options()
    
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    
    if app_path:
        options.app = app_path
    else:
        # Use installed app
        options.app_package = "com.example.flowershop"
        options.app_activity = "com.example.flowershop.MainActivity"
        options.no_reset = True
    
    # For emulator
    options.device_name = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
    
    return options

def _perform_login(android_driver, email, password):
    wait = WebDriverWait(android_driver, 10)

    # Wait for auth screen
    wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Flower Shop')]")))

    # Find input fields
    inputs = android_driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
    if inputs and len(inputs) >= 2:
        email_el, password_el = inputs[0], inputs[1]
    else:
        email_el = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[1]")))
        password_el = android_driver.find_element(AppiumBy.XPATH, "//android.widget.EditText[2]")

    # Populate fields robustly
    try:
        email_el.clear(); email_el.set_value(email)
    except Exception:
        try: email_el.send_keys(email)
        except Exception: pass
    try:
        password_el.clear(); password_el.set_value(password)
    except Exception:
        try: password_el.send_keys(password)
        except Exception: pass

    try:
        android_driver.hide_keyboard()
    except Exception:
        pass

    # Locate clickable login button (ancestor) then click with retries
    try:
        login_btn = WebDriverWait(android_driver, 5).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text,'Login')]/ancestor::*[@clickable='true'][1]"))
        )
    except Exception:
        try:
            login_btn = android_driver.find_element(AppiumBy.XPATH, "//*[@text='Login']")
        except Exception:
            login_btn = None

    if not login_btn:
        return False

    # Try clicking the login button up to 3 times
    for _ in range(3):
        try:
            login_btn.click()
        except Exception:
            try:
                # fallback: tap center coordinates
                loc = login_btn.location; size = login_btn.size
                x = loc['x'] + size['width'] // 2
                y = loc['y'] + size['height'] // 2
                android_driver.execute_script('mobile: clickGesture', {'x': x, 'y': y})
            except Exception:
                pass
        time.sleep(1)
        # Check for home indicator
        try:
            home = WebDriverWait(android_driver, 2).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]") )
            )
            if home:
                return True
        except Exception:
            pass

    # If still not logged in, try alternative login locators and capture debug artifacts
    alt_locators = [
        (AppiumBy.ACCESSIBILITY_ID, "Login"),
        (AppiumBy.XPATH, "//*[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign in')]") ,
        (AppiumBy.XPATH, "//*[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'log in')]") ,
        (AppiumBy.XPATH, "//*[contains(@resource-id,'login')]")
    ]
    for by, val in alt_locators:
        try:
            alt = android_driver.find_element(by, val)
            try:
                alt.click()
            except Exception:
                try:
                    loc = alt.location; size = alt.size
                    x = loc['x'] + size['width'] // 2
                    y = loc['y'] + size['height'] // 2
                    android_driver.execute_script('mobile: clickGesture', {'x': x, 'y': y})
                except Exception:
                    pass
            time.sleep(1)
            try:
                home = WebDriverWait(android_driver, 2).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]"))
                )
                if home:
                    return True
            except Exception:
                pass
        except Exception:
            continue

    # Capture page source and screenshot for debugging
    try:
        ts = int(time.time())
        png = f"/tmp/login_fail_{ts}.png"
        xml = f"/tmp/login_fail_{ts}.xml"
        try:
            android_driver.save_screenshot(png)
        except Exception:
            pass
        try:
            with open(xml, 'w', encoding='utf-8') as f:
                f.write(android_driver.page_source)
        except Exception:
            pass
        print(f"DEBUG: saved screenshot {png} and page source {xml}")
    except Exception:
        pass

    return False


class TestLoginFlow:
    """Tests for the login flow."""
    
    @pytest.fixture
    def logged_in_driver(self, android_driver):
        """Fixture that logs in before each test using the robust helper."""
        # Inject token into app DataStore via broadcast (for debug builds that include TestTokenReceiver)
        token_resp = requests.post("http://localhost:8000/token", data={"username":"test@example.com","password":"testpassword123"})
        token = token_resp.json().get("access_token")
        if token:
            # attempt to set token via Appium mobile shell broadcast (works on emulators or devices supporting shell)
            try:
                android_driver.execute_script('mobile: shell', { 'command': 'am', 'args': ['broadcast','-a','com.example.flowershop.SET_TEST_TOKEN','--es','token', token] })
            except Exception:
                pass

        success = _perform_login(android_driver, "test@example.com", "testpassword123")
        if not success:
            pytest.fail("Could not log in within allotted attempts")
        # ensure home loaded
        wait = WebDriverWait(android_driver, 10)
        wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text,'Welcome')]") ))
        return android_driver

    def test_successful_login(self, logged_in_driver):
        """Test that a user can successfully log in."""
        # Just verify we're on the home screen
        wait = WebDriverWait(logged_in_driver, 10)
        # Check for an element that indicates we're on the home screen
        home_indicator = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]"))
        )
        assert home_indicator.is_displayed()


class TestHomeScreen:
    """Tests for the home/products screen (requires authentication)."""
    
    @pytest.fixture
    def logged_in_driver(self, android_driver):
        """Fixture that logs in before each test using the robust helper."""
        # Inject token into app DataStore via broadcast (for debug builds that include TestTokenReceiver)
        token_resp = requests.post("http://localhost:8000/token", data={"username":"test@example.com","password":"testpassword123"})
        token = token_resp.json().get("access_token")
        if token:
            # attempt to set token via Appium mobile shell broadcast (works on emulators or devices supporting shell)
            try:
                android_driver.execute_script('mobile: shell', { 'command': 'am', 'args': ['broadcast','-a','com.example.flowershop.SET_TEST_TOKEN','--es']['token', token] })
            except Exception:
                pass

        success = _perform_login(android_driver, "test@example.com", "testpassword123")
        if not success:
            pytest.fail("Could not log in within allotted attempts")
        # ensure home loaded
        wait = WebDriverWait(android_driver, 10)
        wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Our Products') or contains(@text,'Welcome')]") ))
        return android_driver

    def test_add_product_to_cart(self, logged_in_driver):
        """Test adding a product to the cart."""
        wait = WebDriverWait(logged_in_driver, 10)
        
        # Find first "Add to Cart" button
        add_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "(//*[contains(@text, 'Add to Cart')])[1]"))
        )
        add_button.click()
        
        # Verify cart badge appears or increments
        time.sleep(1)  # Wait for UI update
        
        # Look for badge on cart icon (should show "1" or similar)
        badge = logged_in_driver.find_elements(AppiumBy.XPATH, "//*[@text='1']")
        assert len(badge) > 0, "Cart badge should show item count"
