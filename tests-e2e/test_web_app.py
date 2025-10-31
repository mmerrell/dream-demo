import pytest

def test_frontend_loads(driver):
    driver.get("http://localhost:3000")
    assert "React App" in driver.title
    assert "Flower Shop" in driver.page_source
