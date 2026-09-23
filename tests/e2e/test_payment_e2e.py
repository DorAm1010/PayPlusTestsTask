"""Combined end-to-end test (Task 4): generate a payment link via the API,
pay it through the real hosted payment page with Selenium, then confirm
the resulting transaction via the API.

Requires the locators in src/ui/pages/payment_page.py to be filled in
against the real page first - see that file's module docstring.
"""

import pytest

from src.api.payloads import generate_link_payload
from src.ui.pages.payment_page import PaymentPage
from src.utils.cards import SUCCESSFUL_CARD

pytestmark = pytest.mark.e2e

E2E_AMOUNT = 50


class TestPaymentEndToEnd:
    def test_full_payment_flow(self, api_client, config, driver, more_info):
        # 1. API: generate a payment link for 50 ILS.
        create_payload = generate_link_payload(
            config.payment_page_uid, amount=E2E_AMOUNT, more_info=more_info
        )
        create_response = api_client.generate_payment_link(create_payload)
        assert create_response.status_code == 200
        create_body = create_response.json()
        assert create_body["results"]["status"] == "success"
        payment_link = create_body["data"]["payment_page_link"]

        # 2-4. Selenium: open the link, fill in the sandbox card, submit.
        page = PaymentPage(driver, timeout=config.ui_timeout)
        page.open(payment_link)
        page.fill_card_details(**SUCCESSFUL_CARD)
        page.submit()

        # 5. Selenium: verify the success message is displayed.
        assert page.is_payment_successful()

        # 6. API: look up the transaction. generateLink never returns a
        # transaction_uid (only page_request_uid), so the more_info value
        # set on the request is used as the correlation key instead.
        view_response = api_client.view_transaction({"more_info": more_info})
        assert view_response.status_code == 200
        view_body = view_response.json()
        assert view_body["results"]["status"] == "success"
        transactions = view_body["data"]
        assert transactions, "No transaction found for the generated more_info id"
        transaction = transactions[0]["transaction"]

        # 7. Assert status_code is "000" and the amount matches what was sent.
        assert transaction["status_code"] == "000"
        assert float(transaction["amount"]) == pytest.approx(E2E_AMOUNT)
