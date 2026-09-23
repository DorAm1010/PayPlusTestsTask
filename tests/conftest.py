import pytest

from src.api.client import PayPlusApiClient
from src.config import load_config
from src.ui.driver_factory import build_chrome_driver
from src.utils.ids import unique_more_info


@pytest.fixture(scope="session")
def config():
    return load_config()


@pytest.fixture(scope="session")
def api_client(config):
    return PayPlusApiClient(config)


@pytest.fixture
def driver(config):
    drv = build_chrome_driver(headless=config.headless)
    yield drv
    drv.quit()


@pytest.fixture
def more_info():
    """A fresh correlation id per test, used both as the more_info sent to
    generateLink and as the lookup key for Transactions/View.
    """
    return unique_more_info()
