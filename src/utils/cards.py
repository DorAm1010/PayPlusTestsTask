"""Sandbox credit card numbers.

Source: https://docs.payplus.co.il/reference/sandbox-credit-card-numbers

The payment page's "holder-identifier" field (not documented alongside the
sandbox cards) expects an Israeli ID number and validates its checksum
client-side, so a random 9-digit string is rejected. DUMMY_CARDHOLDER_ID
below passes that checksum; it identifies no one and is used only to get
past client-side validation in this sandbox.
"""

DUMMY_CARDHOLDER_ID = "104332184"

SUCCESSFUL_CARD = {
    "number": "5326140280779844",
    "expiry": "05/30",
    "cvv": "000",
    "cardholder_id": DUMMY_CARDHOLDER_ID,
}

REJECTED_CARD = {
    "number": "5326140200010120",
    "expiry": "05/30",
    "cvv": "000",
    "cardholder_id": DUMMY_CARDHOLDER_ID,
}
