"""Thin HTTP client for the PayPlus REST API endpoints used by these tests.

See: https://docs.payplus.co.il/reference/post_paymentpages-generatelink
     https://docs.payplus.co.il/reference/post_transactions-view
"""

import requests

from src.config import Config

HEADER_API_KEY = "api-key"
HEADER_SECRET_KEY = "secret-key"
HEADER_CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_JSON = "application/json"

GENERATE_LINK_PATH = "/PaymentPages/generateLink"
VIEW_TRANSACTION_PATH = "/Transactions/View"


class PayPlusApiClient:
    """Wraps the two PayPlus REST endpoints this suite needs, sending the
    api-key/secret-key headers PayPlus's auth scheme requires on every call.
    """

    def __init__(self, config: Config):
        self._base_url = config.api_base_url
        self._session = requests.Session()
        self._session.headers.update(
            {
                HEADER_API_KEY: config.api_key,
                HEADER_SECRET_KEY: config.secret_key,
                HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
            }
        )

    def generate_payment_link(self, payload: dict) -> requests.Response:
        return self._session.post(f"{self._base_url}{GENERATE_LINK_PATH}", json=payload)

    def view_transaction(self, payload: dict) -> requests.Response:
        return self._session.post(f"{self._base_url}{VIEW_TRANSACTION_PATH}", json=payload)
