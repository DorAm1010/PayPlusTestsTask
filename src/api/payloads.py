"""Request body builders for the PayPlus API, kept separate from the tests
so every test starts from the same valid baseline and only overrides what
it actually wants to exercise.
"""

from typing import Optional


def generate_link_payload(
    payment_page_uid: str,
    amount,
    currency_code: str = "ILS",
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
        "payment_page_uid": payment_page_uid,
        "amount": amount,
        "currency_code": currency_code,
        "sendEmailApproval": False,
        "sendEmailFailure": False,
        # Requested so the page renders in English, but this wasn't confirmed
        # to take effect against the real sandbox page (it still rendered
        # dir="rtl" lang="he") - kept anyway since it's harmless, but the
        # Selenium locators are ID-based and don't depend on it.
        "language_code": "en",
    }
    if more_info:
        payload["more_info"] = more_info
    payload.update(overrides)
    return payload
