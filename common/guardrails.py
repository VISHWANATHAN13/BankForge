import re
from html import unescape


CUSTOMER_ID_PATTERN = re.compile(r"^CUS-\d{5}$")
ACCOUNT_ID_PATTERN = re.compile(r"^ACC-\d{5}$")
PRODUCT_ID_PATTERN = re.compile(r"^PROD-[A-Z]{2}-\d{2}$")
APPLICATION_ID_PATTERN = re.compile(r"^APP-\d{5}$")


def validate_customer_id(customer_id: str) -> bool:
    return bool(CUSTOMER_ID_PATTERN.fullmatch(customer_id))


def validate_account_id(account_id: str) -> bool:
    return bool(ACCOUNT_ID_PATTERN.fullmatch(account_id))


def validate_product_id(product_id: str) -> bool:
    return bool(PRODUCT_ID_PATTERN.fullmatch(product_id))


def validate_application_id(application_id: str) -> bool:
    return bool(APPLICATION_ID_PATTERN.fullmatch(application_id))


def mask_account_number(account_number: str) -> str:
    """
    Expose only the last four digits of an account number.
    """

    if not account_number:
        return account_number

    return f"****{account_number[-4:]}"


def redact_for_logging(value):
    """
    Remove/mask sensitive values before they reach logs.
    """

    if isinstance(value, dict):
        redacted = {}

        for key, item in value.items():
            if key.lower() in {
                "account_number",
                "customer_name",
                "message",
                "phone",
                "email",
                "customer_id",
                "account_id",
            }:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_for_logging(item)

        return redacted

    if isinstance(value, list):
        return [redact_for_logging(item) for item in value]

    return value

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?system\s+instructions?", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?developer\s+instructions?", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"developer\s+message", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?(system|developer)\s+prompt", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"act\s+as\s+(an?\s+)?(?:admin|developer|system)", re.IGNORECASE),
]


def sanitize_free_text(value: str, max_length: int = 1000) -> str:
    if value is None:
        return ""

    value = str(value).strip()

    if len(value) > max_length:
        raise ValueError(
            f"Input exceeds maximum allowed length of {max_length} characters."
        )

    # Remove HTML/XML tags.
    value = re.sub(r"<[^>]*>", "", value)

    # Decode HTML entities such as &lt; and &gt;.
    value = unescape(value)

    for pattern in INJECTION_PATTERNS:
        if pattern.search(value):
            raise ValueError("Potential prompt injection detected.")

    return value.strip()