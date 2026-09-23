"""Loads test configuration from environment variables / a .env file."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

ENV_API_KEY = "PAYPLUS_API_KEY"
ENV_SECRET_KEY = "PAYPLUS_SECRET_KEY"
ENV_PAYMENT_PAGE_UID = "PAYPLUS_PAYMENT_PAGE_UID"
ENV_API_BASE_URL = "PAYPLUS_API_BASE_URL"
ENV_HEADLESS = "HEADLESS"
ENV_UI_TIMEOUT = "UI_TIMEOUT"

DEFAULT_API_BASE_URL = "https://restapidev.payplus.co.il/api/v1.0"
DEFAULT_HEADLESS = True
DEFAULT_UI_TIMEOUT = 20

_TRUTHY_VALUES = {"1", "true", "yes", "on"}


def _get_bool(name: str, default: bool) -> bool:
    """Reads a boolean environment variable; unset falls back to `default`."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in _TRUTHY_VALUES


@dataclass(frozen=True)
class Config:
    api_base_url: str
    api_key: str
    secret_key: str
    payment_page_uid: str
    headless: bool
    ui_timeout: int


def load_config() -> Config:
    """Builds a Config from environment variables (already loaded from
    .env by load_dotenv() above). Raises RuntimeError with a clear message
    if the required PayPlus credentials aren't set.
    """
    try:
        api_key = os.environ[ENV_API_KEY]
        secret_key = os.environ[ENV_SECRET_KEY]
        payment_page_uid = os.environ[ENV_PAYMENT_PAGE_UID]
    except KeyError as missing:
        raise RuntimeError(
            f"Missing required environment variable {missing}. "
            "Copy .env.example to .env and fill in the real values."
        ) from missing

    return Config(
        api_base_url=os.getenv(ENV_API_BASE_URL, DEFAULT_API_BASE_URL).rstrip("/"),
        api_key=api_key,
        secret_key=secret_key,
        payment_page_uid=payment_page_uid,
        headless=_get_bool(ENV_HEADLESS, DEFAULT_HEADLESS),
        ui_timeout=int(os.getenv(ENV_UI_TIMEOUT, str(DEFAULT_UI_TIMEOUT))),
    )
