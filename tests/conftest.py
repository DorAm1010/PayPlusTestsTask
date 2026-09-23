import os

import pytest

from src.api.client import PayPlusApiClient
from src.config import load_config
from src.ui.driver_factory import build_chrome_driver
from src.utils.ids import unique_more_info

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "debug_artifacts")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stashes each phase's report on the test item so the `driver` fixture
    can tell, during its own teardown, whether the test it served just
    failed - `yield` inside a fixture doesn't get that information any
    other way.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def config():
    return load_config()


@pytest.fixture(scope="session")
def api_client(config):
    return PayPlusApiClient(config)


@pytest.fixture
def driver(request, config):
    drv = build_chrome_driver(headless=config.headless)
    yield drv

    call_report = getattr(request.node, "rep_call", None)
    if call_report is not None and call_report.failed:
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        name = request.node.name.replace(os.sep, "_")
        screenshot_path = os.path.join(ARTIFACTS_DIR, f"{name}.png")
        html_path = os.path.join(ARTIFACTS_DIR, f"{name}.html")
        try:
            current_url = drv.current_url
            drv.save_screenshot(screenshot_path)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(drv.page_source)
            print(f"\n[UI FAILURE] current_url={current_url}")
            print(f"[UI FAILURE] screenshot saved to {screenshot_path}")
            print(f"[UI FAILURE] page source saved to {html_path}")
        except Exception as exc:
            print(f"\n[UI FAILURE] could not capture debug artifacts: {exc}")

    drv.quit()


@pytest.fixture
def more_info():
    """A fresh correlation id per test, used both as the more_info sent to
    generateLink and as the lookup key for Transactions/View.
    """
    return unique_more_info()
