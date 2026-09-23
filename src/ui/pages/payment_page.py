"""Page object for the PayPlus hosted payment page
(https://paymentsdev.payplus.co.il/<page_request_uid>).

Locators below were captured from the real rendered DOM of a live sandbox
payment page (the "default5" template) - the card form is NOT inside an
iframe, it sits directly in the main document.

*** KNOWN GAP - READ BEFORE RUNNING UI/E2E TESTS ***
The post-submit success/error DOM was not available when this was written,
so SUCCESS_INDICATOR and ERROR_INDICATOR are still placeholders. Before
running any ui/e2e test:

  1. Submit a real payment with the successful sandbox card and inspect the
     resulting DOM (right-click the success message -> Inspect).
  2. Replace SUCCESS_INDICATOR (and ERROR_INDICATOR, using the rejected
     sandbox card) below with the real selectors.

Everything else (field IDs, waits, page flow) is verified against the real
page and ready to use as-is.
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

    # TODO: verify against the real post-submit page (see module docstring)
    SUCCESS_INDICATOR: Locator = (By.CSS_SELECTOR, "TODO_success_message_selector")
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
        Select(self.driver.find_element(*self.CARD_EXPIRY_MONTH_SELECT)).select_by_value(month)
        Select(self.driver.find_element(*self.CARD_EXPIRY_YEAR_SELECT)).select_by_value(year)
        self.driver.find_element(*self.CARD_CVV_INPUT).send_keys(cvv)
        if cardholder_id:
            self.driver.find_element(*self.CARDHOLDER_ID_INPUT).send_keys(cardholder_id)
        Select(self.driver.find_element(*self.INSTALLMENTS_SELECT)).select_by_value(installments)
        return self

    def submit(self) -> "PaymentPage":
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON)).click()
        return self

    def is_payment_successful(self) -> bool:
        return bool(self.wait.until(EC.visibility_of_element_located(self.SUCCESS_INDICATOR)))

    def get_success_text(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.SUCCESS_INDICATOR)).text

    def is_payment_rejected(self) -> bool:
        return bool(self.wait.until(EC.visibility_of_element_located(self.ERROR_INDICATOR)))
