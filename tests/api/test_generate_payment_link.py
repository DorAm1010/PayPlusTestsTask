"""API tests for PaymentPages/generateLink.

https://docs.payplus.co.il/reference/post_paymentpages-generatelink
"""

import pytest

from src.api.payloads import generate_link_payload

pytestmark = pytest.mark.api


def _is_error_response(response) -> bool:
    """The docs only document one error example (422 / "can-not-find-
    payment-page" for an invalid payment_page_uid) and don't give an
    explicit error body for every invalid-input case, so this checks the
    two things every PayPlus error response is expected to satisfy: a
    non-2xx HTTP status, or a results.status that isn't "success".
    """
    if response.status_code >= 400:
        return True
    body = response.json()
    return body.get("results", {}).get("status") != "success"


class TestGeneratePaymentLink:
    def test_valid_data_returns_success_link(self, api_client, config, more_info):
        payload = generate_link_payload(config.payment_page_uid, amount=25, more_info=more_info)

        response = api_client.generate_payment_link(payload)

        assert response.status_code == 200
        body = response.json()
        assert body["results"]["status"] == "success"
        assert body["data"]["payment_page_link"]

    def test_zero_amount_returns_error(self, api_client, config, more_info):
        payload = generate_link_payload(config.payment_page_uid, amount=0, more_info=more_info)

        response = api_client.generate_payment_link(payload)

        assert _is_error_response(response)

    def test_missing_payment_page_uid_returns_error(self, api_client, more_info):
        payload = generate_link_payload("placeholder-uid", amount=25, more_info=more_info)
        del payload["payment_page_uid"]

        response = api_client.generate_payment_link(payload)

        assert _is_error_response(response)

    @pytest.mark.parametrize("amount", [10, 99.99, 500])
    def test_parametrized_amounts_return_valid_link(self, api_client, config, more_info, amount):
        payload = generate_link_payload(
            config.payment_page_uid, amount=amount, more_info=f"{more_info}-{amount}"
        )

        response = api_client.generate_payment_link(payload)

        assert response.status_code == 200
        body = response.json()
        assert body["results"]["status"] == "success"
        assert body["data"]["payment_page_link"]
