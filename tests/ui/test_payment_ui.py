"""UI test: generate a payment link via the API, then pay via the hosted
payment page with Selenium using a sandbox credit card.

Requires the locators in src/ui/pages/payment_page.py to be filled in
against the real page first - see that file's module docstring.
"""

import pytest

from src.api.payloads import generate_link_payload
from src.ui.pages.payment_page import PaymentPage
from src.utils.cards import SUCCESSFUL_CARD

pytestmark = pytest.mark.ui


class TestPaymentUi:
    def test_successful_payment_via_ui(self, api_client, config, driver, more_info):
        payload = generate_link_payload(config.payment_page_uid, amount=25, more_info=more_info)
        response = api_client.generate_payment_link(payload)
        assert response.status_code == 200
        payment_link = response.json()["data"]["payment_page_link"]

        page = PaymentPage(driver, timeout=config.ui_timeout)
        page.open(payment_link)
        page.fill_card_details(**SUCCESSFUL_CARD)
        page.submit()

        assert page.is_payment_successful()
