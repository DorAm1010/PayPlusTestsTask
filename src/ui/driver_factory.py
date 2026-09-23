from selenium import webdriver
from selenium.webdriver.chrome.options import Options

HEADLESS_ARG = "--headless=new"
WINDOW_SIZE_ARG = "--window-size=1400,1000"
DISABLE_GPU_ARG = "--disable-gpu"
NO_SANDBOX_ARG = "--no-sandbox"


def build_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """Build a Chrome WebDriver. Uses Selenium Manager (built into Selenium
    4.6+) to resolve chromedriver automatically, so no separate driver
    binary or webdriver-manager dependency is needed.
    """
    options = Options()
    if headless:
        options.add_argument(HEADLESS_ARG)
    options.add_argument(WINDOW_SIZE_ARG)
    options.add_argument(DISABLE_GPU_ARG)
    options.add_argument(NO_SANDBOX_ARG)
    return webdriver.Chrome(options=options)
