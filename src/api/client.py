"""Thin HTTP client for the PayPlus REST API endpoints used by these tests.

See: https://docs.payplus.co.il/reference/post_paymentpages-generatelink
     https://docs.payplus.co.il/reference/post_transactions-view
"""

import requests

from src.config import Config


class PayPlusApiClient:
    def __init__(self, config: Config):
        self._base_url = config.api_base_url
        self._session = requests.Session()
        self._session.headers.update(
            {
                "api-key": config.api_key,
                "secret-key": config.secret_key,
                "Content-Type": "application/json",
            }
        )

    def generate_payment_link(self, payload: dict) -> requests.Response:
        return self._session.post(f"{self._base_url}/PaymentPages/generateLink", json=payload)

    def view_transaction(self, payload: dict) -> requests.Response:
        return self._session.post(f"{self._base_url}/Transactions/View", json=payload)
