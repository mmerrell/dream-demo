"""
Android E2E Tests for Flower Shop App

These tests cover the main user flows:
- Authentication (login/register)
- Browsing products
- Adding items to cart
- Viewing orders

Run with Sauce Labs:
    SAUCE_USERNAME=xxx SAUCE_ACCESS_KEY=xxx pytest test_android_app.py -v

Run locally (requires Appium server + emulator):
    pytest test_android_app.py -v
"""

import pytest
import time
import requests
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import the android_driver fixture
pytest_plugins = ["conftest_android"]


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


class TestAuthScreen:
    """Tests for the authentication screen."""
    
    def test_auth_screen_elements_visible(self, android_driver):
        """Verify all auth screen elements are displayed."""
        wait = WebDriverWait(android_driver, 15)
        
        # Wait for app to load - look for "Flower Shop" title
        title = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Flower Shop')]"))
        )
        assert title.is_displayed()
        
        # Check for email field
        email_field = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Email')]"))
        )
        assert email_field.is_displayed()
        
        # Check for password field
        password_field = android_driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Password')]")
        assert password_field.is_displayed()
        
        # Check for login button
        login_button = android_driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Login')]")
        assert login_button.is_displayed()
    
    def test_toggle_between_login_and_register(self, android_driver):
        """Test switching between login and register modes."""
        wait = WebDriverWait(android_driver, 15)
        
        # Wait for app to load
        wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Flower Shop')]"))
        )
        
        # Find and click the toggle button
        toggle_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, \"Don't have an account\")]"))
        )
        toggle_button.click()
        
        # Verify we're now in register mode
        time.sleep(0.5)  # Brief wait for UI update
        register_button = android_driver.find_element(AppiumBy.XPATH, "//*[@text='Register']")
        assert register_button.is_displayed()
        
        # Toggle back to login
        toggle_back = android_driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Already have an account')]")
        toggle_back.click()
        
        time.sleep(0.5)
        # Find clickable Login button (some devices expose only text element)
        try:
            login_button = WebDriverWait(android_driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text,'Login')]/ancestor::*[@clickable='true'][1]"))
            )
        except Exception:
            login_button = android_driver.find_element(AppiumBy.XPATH, "//*[@text='Login']")
        login_button.click()


        try:
            home_indicator = wait.until(
                EC.presence_of_element_located((
                    AppiumBy.XPATH,
                    "//*[contains(@text, 'Our Products') or contains(@text, 'Welcome')]"
                ))
            )
            assert home_indicator.is_displayed()
        except TimeoutException:
            errors = android_driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'error') or contains(@text, 'Error')]")
            if errors:
                pytest.fail(f"Login failed with error: {errors[0].text}")
            else:
                pytest.fail("Login did not navigate to home screen")
    
    def test_login_with_invalid_credentials(self, android_driver):
        """Test login fails gracefully with invalid credentials."""
        wait = WebDriverWait(android_driver, 15)
        
        # Wait for auth screen
        wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Flower Shop')]"))
        )
        
        # Enter invalid credentials
        email_fields = android_driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        email_field = email_fields[0] if email_fields else android_driver.find_element(AppiumBy.XPATH, "//android.widget.EditText[1]")
        password_field = email_fields[1] if len(email_fields) > 1 else android_driver.find_element(AppiumBy.XPATH, "//android.widget.EditText[2]")
        
        email_field.click()
        email_field.send_keys("invalid@example.com")
        
        password_field.click()
        password_field.send_keys("wrongpassword")
        
        try:
            android_driver.hide_keyboard()
        except Exception:
            pass

        login_button = android_driver.find_element(AppiumBy.XPATH, "//*[@text='Login']")
        login_button.click()
        
        # Should still be on auth screen (not navigated away)
        time.sleep(2)  # Wait for API response
        
        # Verify we're still on auth screen
        auth_elements = android_driver.find_elements(AppiumBy.XPATH, "//*[@text='Login']")
        assert len(auth_elements) > 0, "Should still be on auth screen after failed login"


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
    
    def test_products_displayed(self, logged_in_driver):
        """Verify products are displayed on home screen."""
        wait = WebDriverWait(logged_in_driver, 10)
        
        # Check for product cards (should have price with $ and Add to Cart button)
        products = wait.until(
            EC.presence_of_all_elements_located((AppiumBy.XPATH, "//*[contains(@text, 'Add to Cart')]"))
        )
        
        assert len(products) > 0, "Should display at least one product"
    
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
    
    def test_navigate_to_cart(self, logged_in_driver):
        """Test navigation to cart screen."""
        wait = WebDriverWait(logged_in_driver, 10)
        
        # Find cart icon (has content description "Cart")
        cart_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Cart"))
        )
        cart_button.click()
        
        # Verify we're on cart screen
        cart_title = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Cart') or contains(@text, 'Shopping')]"))
        )
        assert cart_title.is_displayed()
    
    def test_navigate_to_orders(self, logged_in_driver):
        """Test navigation to orders screen."""
        wait = WebDriverWait(logged_in_driver, 10)
        
        # Find orders icon (has content description "Orders")
        orders_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Orders"))
        )
        orders_button.click()
        
        # Verify we're on orders screen
        orders_indicator = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Order')]"))
        )
        assert orders_indicator.is_displayed()
    
    def test_logout(self, logged_in_driver):
        """Test logout functionality."""
        wait = WebDriverWait(logged_in_driver, 10)
        
        # Find logout icon (has content description "Logout")
        logout_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Logout"))
        )
        logout_button.click()
        
        # Should return to auth screen
        login_button = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='Login']"))
        )
        assert login_button.is_displayed()


class TestCartFlow:
    """Tests for the shopping cart functionality."""
    
    @pytest.fixture
    def logged_in_with_cart_item(self, android_driver):
        """Log in and add an item to cart."""
        wait = WebDriverWait(android_driver, 15)
        
        # Login
        wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Flower Shop')]"))
        )
        
        email_fields = android_driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        if email_fields:
            email_fields[0].send_keys("test@example.com")
            email_fields[1].send_keys("testpassword123")
        
        try:
            android_driver.hide_keyboard()
        except Exception:
            pass

        android_driver.find_element(AppiumBy.XPATH, "//*[@text='Login']").click()
        
        # Wait for home screen and add item to cart
        wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, 'Our Products')]"))
        )
        
        add_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "(//*[contains(@text, 'Add to Cart')])[1]"))
        )
        add_button.click()
        time.sleep(0.5)
        
        return android_driver
    
    def test_cart_shows_added_items(self, logged_in_with_cart_item):
        """Verify added items appear in cart."""
        wait = WebDriverWait(logged_in_with_cart_item, 10)
        
        # Navigate to cart
        cart_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Cart"))
        )
        cart_button.click()
        
        # Should see item in cart with quantity and total
        time.sleep(1)
        
        # Look for price total or item details
        cart_content = logged_in_with_cart_item.find_elements(
            AppiumBy.XPATH, 
            "//*[contains(@text, '$') or contains(@text, 'Total')]"
        )
        assert len(cart_content) > 0, "Cart should show items with prices"
