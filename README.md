# PayPlus Payment Flow — Automated Tests

Pytest project automating the PayPlus payment flow: generating a payment
link via the REST API, paying it through the hosted payment page with
Selenium, and confirming the resulting transaction via the API.

## ⚠️ Before running the UI or E2E tests

The Selenium locators in
[`src/ui/pages/payment_page.py`](src/ui/pages/payment_page.py) for the
**payment form itself** (cardholder name, card number, expiry month/year,
CVV, the Israeli ID field, installments, submit button) and for the
**post-submit success page** (`SUCCESS_INDICATOR`) were captured from the
real rendered DOM of a live sandbox payment run and are verified — there is
no iframe around the form.

What's still a placeholder: `ERROR_INDICATOR`, since a rejected-payment DOM
sample wasn't available while building this (none of the 4 required tests
exercise `is_payment_rejected()`, so this doesn't block running the suite).
To fill it in:

1. Run one API test (or call `PaymentPages/generateLink` manually) to get a
   real payment link, open it in Chrome, and submit a payment with the
   **rejected** sandbox card (`REJECTED_CARD` in `src/utils/cards.py`).
2. Right-click the resulting error message and choose **Inspect** to find
   its CSS selector.
3. Replace `ERROR_INDICATOR` in `PaymentPage` with the real selector.

Everything else (waits, page flow, the E2E correlation logic, the rest of
the form fields, success detection) is ready to run as-is.

## Requirements

- Python 3.10
- Google Chrome (Selenium 4's built-in Selenium Manager downloads a
  matching chromedriver automatically — no separate driver install needed)

## Setup

```bash
git clone <this-repo-url>
cd PayPlusTestsTask

python3.10 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Edit `.env` and fill in the real values provided for this test:

```
PAYPLUS_API_KEY=...
PAYPLUS_SECRET_KEY=...
PAYPLUS_PAYMENT_PAGE_UID=...
```

`.env` is gitignored — never commit real credentials.

## Running the tests

```bash
pytest                 # everything
pytest -m api           # Task 2 only — API tests, no browser
pytest -m ui             # Task 3 only — Selenium UI test
pytest -m e2e            # Task 4 only — combined API + Selenium flow
```

Tests are also grouped by directory (`tests/api`, `tests/ui`, `tests/e2e`)
if you'd rather select that way, e.g. `pytest tests/api`.

Set `HEADLESS=false` in `.env` to watch the browser during UI/E2E runs
instead of running headless.

## Project structure

```
src/
  config.py              # loads settings from .env
  api/
    client.py             # PayPlusApiClient — generateLink / view calls
    payloads.py            # builds valid request bodies for generateLink
  ui/
    driver_factory.py       # builds the Chrome WebDriver
    pages/payment_page.py    # page object for the hosted payment page
  utils/
    ids.py                   # unique more_info correlation id generator
    cards.py                  # sandbox credit card numbers

tests/
  conftest.py             # shared fixtures: config, api_client, driver, more_info
  api/test_generate_payment_link.py   # Task 2
  ui/test_payment_ui.py                # Task 3
  e2e/test_payment_e2e.py               # Task 4
```

## Assumptions & design decisions

- **Currency**: all amounts (including the parametrized 10 / 99.99 / 500
  and the E2E test's 50) use `ILS`, matching the payment page's default
  currency and the amount given in Task 4.
- **Error assertions (Task 2, tests 2 & 3)**: the docs only give one
  explicit error example (422 `can-not-find-payment-page`, for an invalid
  `payment_page_uid`) and don't document a specific error body for every
  invalid-input case. Both error tests assert the general contract: a
  non-2xx HTTP status, or a JSON body whose `results.status` is not
  `"success"`.
- **`amount: 0` is accepted by the real API, not rejected**: confirmed via
  a live call — `PaymentPages/generateLink` returns a normal 200/success
  response with a real `payment_page_link` for `amount: 0`. This
  contradicts the task's stated expectation, so `test_zero_amount_returns_error`
  is marked `@pytest.mark.xfail(strict=True, ...)` with the confirmed
  response documented in the reason string, rather than forcing a false
  assertion to pass. `strict=True` means if PayPlus's validation is ever
  fixed, the test flips to a reported failure (XPASS) instead of silently
  staying green.
- **Cardholder ID field**: the real payment page has an undocumented
  `holder-identifier` field (an Israeli ID number) that validates its
  checksum client-side. `src/utils/cards.py` includes a checksum-valid
  dummy ID (`DUMMY_CARDHOLDER_ID`) used to fill it.
- **Task 4 transaction lookup**: `PaymentPages/generateLink` only returns a
  `page_request_uid`, never a `transaction_uid`, and there's no reliable
  way to scrape a transaction id off the payment page. Instead, each test
  sets a unique value in the `more_info` field when generating the link,
  then looks the resulting transaction up via `Transactions/View` using
  that same `more_info` value as the correlation key.
- **Emails disabled**: `sendEmailApproval` / `sendEmailFailure` are set to
  `false` in every generated request so test runs don't trigger real
  emails.
- **Language**: `language_code` is requested as `en`, but this wasn't
  confirmed to change the rendered page (it still came back `dir="rtl"
  lang="he"` in testing). Harmless either way since the Selenium locators
  are ID-based, not text-based.
- **MyAccount credentials**: the task lists a MyAccount URL/email/password,
  but none of the 4 required tests need a MyAccount (merchant dashboard)
  login — everything goes through the payment link and the two documented
  API endpoints. These credentials are unused by this suite.
- **Success message locator is verified, error locator is a placeholder** —
  `SUCCESS_INDICATOR` was captured from a real post-submit page and is
  ready to use; `ERROR_INDICATOR` still needs a rejected-payment DOM
  sample. See the warning at the top of this README and the docstring in
  `src/ui/pages/payment_page.py`.
