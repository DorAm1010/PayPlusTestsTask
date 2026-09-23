"""Standalone manual-debugging script for the expiry month/year dropdowns -
NOT part of the test suite (pytest never collects this), and NOT meant to
ship in the final submission zip; delete this file (or the whole scripts/
folder) before zipping up the project.

Run it directly (not through pytest) with a real, visible Chrome window:

    python scripts/manual_debug_dropdown.py

It walks through the same steps fill_card_details()/submit() do, but one
at a time with an `input("Press Enter...")` pause between each, so you can
look at (or manually click into) the browser window at each step before
the script moves on. Requires .env to already be filled in.

Two ways of selecting the month/year are tried back to back on the same
page, printing OK/MISMATCH for each, so you can directly compare them:

  click_select_option() - click the <select> to open it, scroll the
  target <option> into view, click it, then verify. This is the "manual"
  version of what Select().select_by_value() already does internally
  (find the option, click it) - it can hit the exact same Chrome/
  ChromeDriver popup-opens-then-closes-too-fast race Select() did.

  type_select_option() - focuses the <select> and types the option's
  visible text, using the browser's native type-ahead search for <select>
  elements (the same thing that happens if you Tab onto a dropdown and
  start typing). This never opens the native popup at all, so it can't
  hit that race. It only works here because these options' visible text
  happens to equal their value (e.g. "05", "30") - true for this page.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from src.api.client import PayPlusApiClient
from src.api.payloads import generate_link_payload
from src.config import load_config
from src.ui.driver_factory import build_chrome_driver
from src.utils.cards import SUCCESSFUL_CARD
from src.utils.ids import unique_more_info


def click_select_option(driver, wait: WebDriverWait, select_id: str, value: str) -> None:
    select_element = wait.until(EC.element_to_be_clickable((By.ID, select_id)))
    select_element.click()  # opens the native dropdown

    option = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#{select_id} option[value='{value}']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
    option.click()  # selects it (closes the dropdown as a side effect)

    _verify_selected(driver, select_id, value)


def type_select_option(driver, wait: WebDriverWait, select_id: str, value: str) -> None:
    element = wait.until(EC.element_to_be_clickable((By.ID, select_id)))
    element.send_keys(value)

    _verify_selected(driver, select_id, value)


def _verify_selected(driver, select_id: str, value: str) -> None:
    selected = Select(driver.find_element(By.ID, select_id)).first_selected_option.get_attribute("value")
    status = "OK" if selected == value else "MISMATCH"
    print(f"[{status}] #{select_id} value is now {selected!r} (expected {value!r})")


def main() -> None:
    config = load_config()
    api_client = PayPlusApiClient(config)

    payload = generate_link_payload(config.payment_page_uid, amount=25, more_info=unique_more_info())
    response = api_client.generate_payment_link(payload)
    response.raise_for_status()
    payment_link = response.json()["data"]["payment_page_link"]
    print(f"Payment link: {payment_link}")

    driver = build_chrome_driver(headless=False)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(payment_link)
        input("Page loaded - press Enter to fill cardholder name + card number...")

        driver.find_element(By.ID, "card-holder-name").send_keys("QA Automation")
        driver.find_element(By.ID, "credit-card-input").send_keys(SUCCESSFUL_CARD["number"])

        month, year = SUCCESSFUL_CARD["expiry"].split("/")

        input("Press Enter to select month+year via click_select_option() (click/scroll/click/verify)...")
        click_select_option(driver, wait, "expiration-date-month", month)
        click_select_option(driver, wait, "expiration-date-year", year)

        input(
            "Press Enter to RE-select both via type_select_option() instead (keyboard "
            "type-ahead, no popup involved at all) and compare the result..."
        )
        type_select_option(driver, wait, "expiration-date-month", month)
        type_select_option(driver, wait, "expiration-date-year", year)

        input("Press Enter to fill CVV, holder ID, and installments...")
        driver.find_element(By.ID, "cvv-input").send_keys(SUCCESSFUL_CARD["cvv"])
        driver.find_element(By.ID, "holder-identifier").send_keys(SUCCESSFUL_CARD["cardholder_id"])
        Select(driver.find_element(By.ID, "payments")).select_by_value("1")

        input("Form filled - look at the whole form now (placeholder still overlapping?). Press Enter to submit...")
        driver.find_element(By.ID, "credit-card-submit").click()

        input("Submitted - press Enter to close the browser and exit...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
