from pathlib import Path
from data.compliance.database import get_customer
from common.guardrails import validate_customer_id

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "communication_templates"


def get_customer_profile_resource(customer_id: str):
    """
    MCP Resource:
        customer://{customer_id}/profile
    """
    if not validate_customer_id(customer_id):
        return {
        "error": "Invalid customer ID format. Expected CUS-XXXXX."
    }

    customer = get_customer(customer_id)

    if not customer:
        return {
            "error": f"Customer not found: {customer_id}"
        }

    return {
        "customer_id": customer["customer_id"],
        "customer_name": customer["customer_name"],
        "kyc_status": customer["kyc_status"],
        "customer_tier": customer["customer_tier"],
    }


def get_template_resource(template_name: str):
    """
    MCP Resource:
        template://{template_name}
    """

    allowed_templates = {
        "loan_approval.md",
        "loan_rejection.md",
        "transaction_alert.md",
        "kyc_reminder.md",
    }

    if not template_name.endswith(".md"):
        template_name = f"{template_name}.md"

    if template_name not in allowed_templates:
        return {
            "error": f"Unknown communication template: {template_name}"
        }

    template_path = TEMPLATE_DIR / template_name

    if not template_path.exists():
        return {
            "error": f"Template not found: {template_name}"
        }

    return {
        "template_name": template_name,
        "content": template_path.read_text(
            encoding="utf-8"
        ),
    }