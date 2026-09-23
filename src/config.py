"""Loads test configuration from environment variables / a .env file."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    api_base_url: str
    api_key: str
    secret_key: str
    payment_page_uid: str
    headless: bool
    ui_timeout: int


def load_config() -> Config:
    try:
        api_key = os.environ["PAYPLUS_API_KEY"]
        secret_key = os.environ["PAYPLUS_SECRET_KEY"]
        payment_page_uid = os.environ["PAYPLUS_PAYMENT_PAGE_UID"]
    except KeyError as missing:
        raise RuntimeError(
            f"Missing required environment variable {missing}. "
            "Copy .env.example to .env and fill in the real values."
        ) from missing

    return Config(
        api_base_url=os.getenv(
            "PAYPLUS_API_BASE_URL", "https://restapidev.payplus.co.il/api/v1.0"
        ).rstrip("/"),
        api_key=api_key,
        secret_key=secret_key,
        payment_page_uid=payment_page_uid,
        headless=_get_bool("HEADLESS", True),
        ui_timeout=int(os.getenv("UI_TIMEOUT", "20")),
    )
