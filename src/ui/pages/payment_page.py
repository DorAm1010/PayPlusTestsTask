"""Page object for the PayPlus hosted payment page
(https://paymentsdev.payplus.co.il/<page_request_uid>).

Locators below were captured from the real rendered DOM of a live sandbox
payment page (the "default5" template) - the card form is NOT inside an
iframe, it sits directly in the main document. The post-submit "Payment
Successful" page (the redirect target after a successful sandbox payment)
was also captured from a real run and SUCCESS_INDICATOR is verified against
it: `.thank-you-page-container` wraps the whole confirmation view (check
mark, amount, transaction number, etc.) and is a real author-assigned CSS
class, unlike the `data-v-<hash>` scoped-style attributes on the same
elements, which are build artifacts that change every Vue/Quasar rebuild
and are deliberately not used as selectors here.

*** KNOWN GAP - READ BEFORE RUNNING UI/E2E TESTS ***
No rejected-payment DOM sample was available when this was written, so
ERROR_INDICATOR is still a placeholder. To fill it in: submit a payment
with the rejected sandbox card (src/utils/cards.py REJECTED_CARD) and
inspect the resulting DOM, then replace ERROR_INDICATOR below with the
real selector. Nothing in the 4 required tests exercises is_payment_rejected(),
so this gap doesn't block running the suite.

Everything else (field IDs, waits, page flow, the success indicator) is
verified against the real page and ready to use as-is.
"""

from typing import Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

Locator = Tuple[str, str]


class PaymentPage:
    CARDHOLDER_NAME_INPUT: Locator = (By.ID, "card-holder-name")
    CARD_NUMBER_INPUT: Locator = (By.ID, "credit-card-input")
    CARD_EXPIRY_MONTH_SELECT: Locator = (By.ID, "expiration-date-month")
    CARD_EXPIRY_YEAR_SELECT: Locator = (By.ID, "expiration-date-year")
    CARD_CVV_INPUT: Locator = (By.ID, "cvv-input")
    CARDHOLDER_ID_INPUT: Locator = (By.ID, "holder-identifier")
    INSTALLMENTS_SELECT: Locator = (By.ID, "payments")
    SUBMIT_BUTTON: Locator = (By.ID, "credit-card-submit")

    SUCCESS_INDICATOR: Locator = (By.CSS_SELECTOR, ".thank-you-page-container")
    # TODO: verify against a real rejected-payment page (see module docstring)
    ERROR_INDICATOR: Locator = (By.CSS_SELECTOR, "TODO_error_message_selector")

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> "PaymentPage":
        self.driver.get(url)
        return self

    def fill_card_details(
        self,
        number: str,
        expiry: str,
        cvv: str,
        cardholder_name: str = "QA Automation",
        cardholder_id: str = "",
        installments: str = "1",
    ) -> "PaymentPage":
        """expiry is "MM/YY" (e.g. "05/30"), matching the two expiry
        <select> elements' option values on the real page.
        """
        month, year = expiry.split("/")

        self.wait.until(EC.visibility_of_element_located(self.CARDHOLDER_NAME_INPUT)).send_keys(cardholder_name)
        self.driver.find_element(*self.CARD_NUMBER_INPUT).send_keys(number)
        self._select_and_verify(self.CARD_EXPIRY_MONTH_SELECT, month)
        self._select_and_verify(self.CARD_EXPIRY_YEAR_SELECT, year)
        self.driver.find_element(*self.CARD_CVV_INPUT).send_keys(cvv)
        if cardholder_id:
            self.driver.find_element(*self.CARDHOLDER_ID_INPUT).send_keys(cardholder_id)
        self._select_and_verify(self.INSTALLMENTS_SELECT, installments)
        return self

    def _select_and_verify(self, locator: Locator, value: str) -> None:
        """A prior run showed both expiry <select>s flagged with a "required"
        validation error immediately after submit, despite Select() having
        already set their values - the page's own Vue app hadn't registered
        the change yet. Re-selecting and polling the select's own reported
        value (instead of moving on right after one select_by_value() call)
        guards against that race.
        """
        Select(self.driver.find_element(*locator)).select_by_value(value)
        self.wait.until(
            lambda d: Select(d.find_element(*locator)).first_selected_option.get_attribute("value") == value
        )

    def submit(self) -> "PaymentPage":
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON)).click()
        return self

    def is_payment_successful(self) -> bool:
        return bool(self.wait.until(EC.visibility_of_element_located(self.SUCCESS_INDICATOR)))

    def get_success_text(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.SUCCESS_INDICATOR)).text

    def is_payment_rejected(self) -> bool:
        return bool(self.wait.until(EC.visibility_of_element_located(self.ERROR_INDICATOR)))
