"""Page object for the PayPlus hosted payment page
(https://paymentsdev.payplus.co.il/<page_request_uid>).

*** KNOWN GAP - READ BEFORE RUNNING UI/E2E TESTS ***
This project was built without network access to the live payment page (see
README "Known gaps"), so the locators below are PLACEHOLDERS and have not
been verified against the real DOM. Before running any ui/e2e test:

  1. Generate a payment link (e.g. run one api test, or call the API by hand)
     and open it in Chrome.
  2. Right-click each field (card number, expiry, CVV, submit button, the
     success message) -> Inspect, and note its id/name/CSS selector.
  3. Replace every TODO_* value below with the real one. If the card form is
     NOT inside an iframe, set CARD_FORM_IFRAME = None.

Everything else in this class (waits, flow, structure) is ready to use as-is
once the locators are filled in.
"""

from typing import Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = Tuple[str, str]


class PaymentPage:
    # --- Locators: verify against the real page (see module docstring) ---
    CARD_FORM_IFRAME: Optional[Locator] = (By.CSS_SELECTOR, "TODO_iframe_selector")
    CARD_NUMBER_INPUT: Locator = (By.ID, "TODO_card_number_id")
    CARD_EXPIRY_INPUT: Locator = (By.ID, "TODO_card_expiry_id")
    CARD_CVV_INPUT: Locator = (By.ID, "TODO_card_cvv_id")
    CARDHOLDER_NAME_INPUT: Optional[Locator] = (By.ID, "TODO_cardholder_name_id")
    SUBMIT_BUTTON: Locator = (By.CSS_SELECTOR, "TODO_submit_button_selector")
    SUCCESS_INDICATOR: Locator = (By.CSS_SELECTOR, "TODO_success_message_selector")
    ERROR_INDICATOR: Locator = (By.CSS_SELECTOR, "TODO_error_message_selector")

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> "PaymentPage":
        self.driver.get(url)
        return self

    def _enter_card_frame(self) -> None:
        if self.CARD_FORM_IFRAME is None:
            return
        frame = self.wait.until(EC.presence_of_element_located(self.CARD_FORM_IFRAME))
        self.driver.switch_to.frame(frame)

    def _exit_card_frame(self) -> None:
        if self.CARD_FORM_IFRAME is not None:
            self.driver.switch_to.default_content()

    def fill_card_details(
        self, number: str, expiry: str, cvv: str, cardholder_name: str = "QA Automation"
    ) -> "PaymentPage":
        self._enter_card_frame()
        try:
            self.wait.until(EC.visibility_of_element_located(self.CARD_NUMBER_INPUT)).send_keys(number)
            self.driver.find_element(*self.CARD_EXPIRY_INPUT).send_keys(expiry)
            self.driver.find_element(*self.CARD_CVV_INPUT).send_keys(cvv)
            if self.CARDHOLDER_NAME_INPUT is not None:
                self.driver.find_element(*self.CARDHOLDER_NAME_INPUT).send_keys(cardholder_name)
        finally:
            self._exit_card_frame()
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
