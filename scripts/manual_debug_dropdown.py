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

To watch the native <select> popup instead of it closing immediately:
this script opens the month dropdown with a plain `.click()` first (which
just opens the native popup and does NOT pick an option, unlike
Select().select_by_value() which finds-and-clicks the option in one go)
and pauses right after - the popup stays open on screen for as long as
the script is paused, since nothing else is happening to close it. Press
Escape or click elsewhere in the browser to close it manually, or just
press Enter here to let the script continue with the real selection.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from src.api.client import PayPlusApiClient
from src.api.payloads import generate_link_payload
from src.config import load_config
from src.ui.driver_factory import build_chrome_driver
from src.utils.cards import SUCCESSFUL_CARD
from src.utils.ids import unique_more_info


def main() -> None:
    config = load_config()
    api_client = PayPlusApiClient(config)

    payload = generate_link_payload(config.payment_page_uid, amount=25, more_info=unique_more_info())
    response = api_client.generate_payment_link(payload)
    response.raise_for_status()
    payment_link = response.json()["data"]["payment_page_link"]
    print(f"Payment link: {payment_link}")

    driver = build_chrome_driver(headless=False)
    try:
        driver.get(payment_link)
        input("Page loaded - press Enter to fill cardholder name + card number...")

        driver.find_element(By.ID, "card-holder-name").send_keys("QA Automation")
        driver.find_element(By.ID, "credit-card-input").send_keys(SUCCESSFUL_CARD["number"])

        month, year = SUCCESSFUL_CARD["expiry"].split("/")

        month_select = driver.find_element(By.ID, "expiration-date-month")
        month_select.click()  # opens the native popup only, selects nothing
        input(
            "Month dropdown should be open on screen now - look at it (or click an "
            "option yourself with the mouse). Press Enter to continue - this will "
            "try Selenium's real Select().select_by_value() next..."
        )

        Select(month_select).select_by_value(month)
        month_value = Select(driver.find_element(By.ID, "expiration-date-month")).first_selected_option.get_attribute(
            "value"
        )
        print(f"Month select's value is now: {month_value!r} (expected {month!r})")
        input("Press Enter to select the year the same way...")

        year_select = driver.find_element(By.ID, "expiration-date-year")
        Select(year_select).select_by_value(year)
        year_value = Select(driver.find_element(By.ID, "expiration-date-year")).first_selected_option.get_attribute(
            "value"
        )
        print(f"Year select's value is now: {year_value!r} (expected {year!r})")
        input("Press Enter to fill CVV, holder ID, and installments...")

        driver.find_element(By.ID, "cvv-input").send_keys(SUCCESSFUL_CARD["cvv"])
        driver.find_element(By.ID, "holder-identifier").send_keys(SUCCESSFUL_CARD["cardholder_id"])
        Select(driver.find_element(By.ID, "payments")).select_by_value("1")

        input("Form filled - look at the whole form now. Press Enter to submit...")
        driver.find_element(By.ID, "credit-card-submit").click()

        input("Submitted - press Enter to close the browser and exit...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
