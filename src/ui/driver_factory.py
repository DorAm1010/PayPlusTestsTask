from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def build_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """Build a Chrome WebDriver. Uses Selenium Manager (built into Selenium
    4.6+) to resolve chromedriver automatically, so no separate driver
    binary or webdriver-manager dependency is needed.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)
