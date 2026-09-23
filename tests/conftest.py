import dataclasses
import os

import pytest

from src.api.client import PayPlusApiClient
from src.config import load_config
from src.ui.driver_factory import build_chrome_driver
from src.utils.ids import unique_more_info

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "debug_artifacts")

HEADLESS_CLI_OPTION = "--headless"
HEADLESS_CHOICE_TRUE = "true"
HEADLESS_CHOICE_FALSE = "false"


def pytest_addoption(parser):
    parser.addoption(
        HEADLESS_CLI_OPTION,
        action="store",
        default=None,
        choices=[HEADLESS_CHOICE_TRUE, HEADLESS_CHOICE_FALSE],
        help="Override the HEADLESS setting from .env for Selenium UI/E2E tests.",
    )


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
def config(request):
    """Loads Config from .env, then applies --headless if it was passed on
    the command line (takes precedence over the .env HEADLESS value).
    """
    cfg = load_config()
    headless_override = request.config.getoption(HEADLESS_CLI_OPTION)
    if headless_override is not None:
        cfg = dataclasses.replace(cfg, headless=headless_override == HEADLESS_CHOICE_TRUE)
    return cfg


@pytest.fixture(scope="session")
def api_client(config):
    return PayPlusApiClient(config)


@pytest.fixture
def driver(request, config):
    """A function-scoped Chrome WebDriver. On teardown, if the test it
    served failed, saves a screenshot and the page source to
    debug_artifacts/ (gitignored) before quitting, to help diagnose
    UI/E2E failures without a live browser to look at.
    """
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
