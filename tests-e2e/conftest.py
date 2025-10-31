import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os

# Sauce Labs capabilities
SAUCE_USERNAME = os.getenv("SAUCE_USERNAME")
SAUCE_ACCESS_KEY = os.getenv("SAUCE_ACCESS_KEY")

# Ensure SAUCE_USERNAME and SAUCE_ACCESS_KEY are set
if not SAUCE_USERNAME or not SAUCE_ACCESS_KEY:
    raise Exception("SAUCE_USERNAME and SAUCE_ACCESS_KEY environment variables must be set.")

SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.us-west-1.saucelabs.com:443/wd/hub"

@pytest.fixture(params=["chrome", "firefox"], scope="function")
def driver(request):
    browser = request.param
    test_name = request.node.name

    if browser == "chrome":
        options = ChromeOptions()
        options.browser_version = "latest"
        options.platform_name = "Windows 10"
        sauce_options = {
            'build': os.getenv("SAUCE_BUILD_NAME", "DreamDemo-Web-Build-1"),
            'name': test_name,
            'screenResolution': '1280x1024'
        }
    elif browser == "firefox":
        options = FirefoxOptions()
        options.browser_version = "latest"
        options.platform_name = "Windows 10"
        sauce_options = {
            'build': os.getenv("SAUCE_BUILD_NAME", "DreamDemo-Web-Build-1"),
            'name': test_name,
            'screenResolution': '1280x1024'
        }
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    options.set_capability('sauce:options', sauce_options)

    _driver = webdriver.Remote(
        command_executor=SAUCE_URL,
        options=options
    )
    yield _driver
    _driver.quit()
