import uuid


def unique_more_info(prefix: str = "qa") -> str:
    """A short, unique correlation id used to look up a transaction later
    via the more_info field, since generateLink does not return a
    transaction_uid (only a page_request_uid).
    """
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
