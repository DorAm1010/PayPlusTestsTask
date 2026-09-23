"""Request body builders for the PayPlus API, kept separate from the tests
so every test starts from the same valid baseline and only overrides what
it actually wants to exercise.
"""

from typing import Optional

FIELD_PAYMENT_PAGE_UID = "payment_page_uid"
FIELD_AMOUNT = "amount"
FIELD_CURRENCY_CODE = "currency_code"
FIELD_SEND_EMAIL_APPROVAL = "sendEmailApproval"
FIELD_SEND_EMAIL_FAILURE = "sendEmailFailure"
FIELD_LANGUAGE_CODE = "language_code"
FIELD_MORE_INFO = "more_info"

DEFAULT_CURRENCY_CODE = "ILS"
DEFAULT_LANGUAGE_CODE = "en"


def generate_link_payload(
    payment_page_uid: str,
    amount,
    currency_code: str = DEFAULT_CURRENCY_CODE,
    more_info: Optional[str] = None,
    **overrides,
) -> dict:
    """Build a valid PaymentPages/generateLink request body.

    Only the fields required by the docs (payment_page_uid, amount,
    currency_code, sendEmailApproval, sendEmailFailure) are set by default.
    Email sending is disabled by default so test runs don't trigger real
    emails. Pass keyword overrides to add/replace fields, or delete a key
    from the returned dict to test a missing-field scenario.
    """
    payload = {
        FIELD_PAYMENT_PAGE_UID: payment_page_uid,
        FIELD_AMOUNT: amount,
        FIELD_CURRENCY_CODE: currency_code,
        FIELD_SEND_EMAIL_APPROVAL: False,
        FIELD_SEND_EMAIL_FAILURE: False,
        # Requested so the page renders in English, but this wasn't confirmed
        # to take effect against the real sandbox page (it still rendered
        # dir="rtl" lang="he") - kept anyway since it's harmless, but the
        # Selenium locators are ID-based and don't depend on it.
        FIELD_LANGUAGE_CODE: DEFAULT_LANGUAGE_CODE,
    }
    if more_info:
        payload[FIELD_MORE_INFO] = more_info
    payload.update(overrides)
    return payload
