from pathlib import Path
from datetime import datetime

from data.compliance.database import (
    get_customer,
    get_kyc_status,
    get_fraud_flags,
    add_communication,
)
from data.compliance.database import (
    get_customer,
    get_fraud_flags,
    add_communication,
    write_audit_log,
)
from common.guardrails import validate_customer_id
from common.logging_config import get_logger, trace
from common.guardrails import redact_for_logging
from common.guardrails import sanitize_free_text
from common.audit import record_audit_event

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "communication_templates"

@trace(logger, redact=redact_for_logging)
def get_kyc_status_tool(customer_id: str):
    """
    Get the KYC status of a customer.
    """
    if not validate_customer_id(customer_id):
        return {
        "success": False,
        "error": "Invalid customer ID format. Expected CUS-XXXXX.",
    }

    customer = get_customer(customer_id)

    if not customer:
        return {
            "success": False,
            "error": f"Customer not found: {customer_id}",
        }

    return {
        "success": True,
        "customer_id": customer_id,
        "kyc_status": customer["kyc_status"],
    }

@trace(logger, redact=redact_for_logging)
def get_fraud_flags_tool(customer_id: str):
    """
    Retrieve fraud flags associated with a customer.
    """
    if not validate_customer_id(customer_id):
        return {
        "success": False,
        "error": "Invalid customer ID format. Expected CUS-XXXXX.",
    }
        
    customer = get_customer(customer_id)

    if not customer:
        return {
            "success": False,
            "error": f"Customer not found: {customer_id}",
        }

    flags = get_fraud_flags(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(flags),
        "fraud_flags": flags,
    }

@trace(logger, redact=redact_for_logging)
def run_compliance_check_tool(customer_id: str):
    """
    Run a basic compliance check.
    """
    if not validate_customer_id(customer_id):
        return {
        "success": False,
        "error": "Invalid customer ID format. Expected CUS-XXXXX.",
    }

    customer = get_customer(customer_id)

    if not customer:
        return {
            "success": False,
            "error": f"Customer not found: {customer_id}",
        }

    kyc_status = customer["kyc_status"]
    fraud_flags = get_fraud_flags(customer_id)

    open_flags = [
        flag
        for flag in fraud_flags
        if flag["status"].upper() == "OPEN"
    ]

    compliance_passed = (
        kyc_status.upper() == "VERIFIED"
        and len(open_flags) == 0
    )

    return {
        "success": True,
        "customer_id": customer_id,
        "kyc_status": kyc_status,
        "open_fraud_flags": len(open_flags),
        "compliance_passed": compliance_passed,
    }

@trace(logger, redact=redact_for_logging)
def generate_customer_communication_tool(
    template_name: str,
    customer_name: str,
    account_tier: str,
    specific_detail: str,
    **extra_fields,
):
    """
    Generate customer communication from a Markdown template.
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
            "success": False,
            "error": f"Unknown communication template: {template_name}",
        }

    template_path = TEMPLATE_DIR / template_name

    if not template_path.exists():
        return {
            "success": False,
            "error": f"Template not found: {template_name}",
        }

    template = template_path.read_text(encoding="utf-8")

    try:
        safe_customer_name = sanitize_free_text(customer_name, max_length=200)
        safe_account_tier = sanitize_free_text(account_tier, max_length=50)
        safe_specific_detail = sanitize_free_text(specific_detail, max_length=1000)

        safe_extra_fields = {
            key: sanitize_free_text(str(value), max_length=500)
            for key, value in extra_fields.items()
        }

    except ValueError as exc:
        return {
        "success": False,
        "error": str(exc),
    }
    
    fields = {
    "customer_name": safe_customer_name,
    "account_tier": safe_account_tier,
    "specific_detail": safe_specific_detail,
    **safe_extra_fields,
    }

    try:
        message = template.format(**fields)
    except KeyError as exc:
        return {
            "success": False,
            "error": f"Missing template field: {exc.args[0]}",
        }

    return {
        "success": True,
        "template_name": template_name,
        "message": message,
    }

@trace(logger, redact=redact_for_logging)
def send_customer_communication_tool(
    customer_id: str,
    channel: str,
    message: str,
):
    """
    Record a customer communication.
    """
    if not validate_customer_id(customer_id):
        return {
        "success": False,
        "error": "Invalid customer ID format. Expected CUS-XXXXX.",
    }
    
    customer = get_customer(customer_id)

    if not customer:
        return {
            "success": False,
            "error": f"Customer not found: {customer_id}",
        }

    allowed_channels = {
        "EMAIL",
        "SMS",
        "PUSH",
    }

    channel = channel.upper()

    if channel not in allowed_channels:
        return {
            "success": False,
            "error": f"Unsupported communication channel: {channel}",
        }
    
    try:
        safe_message = sanitize_free_text(message, max_length=2000)
    except ValueError as exc:
        return {
        "success": False,
        "error": str(exc),
    }

    communication = add_communication(
    customer_id=customer_id,
    channel=channel,
    message=safe_message,
    sent_at=datetime.now().isoformat(),
    status="SENT",
)
    
    record_audit_event(
    action_type="CUSTOMER_COMMUNICATION_SENT",
    performed_by="MCP_CLIENT",
    customer_id=customer_id,
    outcome="SUCCESS",
    )
    return {
        "success": True,
        "communication": communication,
    }

@trace(logger, redact=redact_for_logging)
def write_audit_log_tool(
    action_type: str,
    performed_by: str,
    customer_id: str,
    outcome: str,
):
    """
    Write a compliance audit log entry.
    """
    if not validate_customer_id(customer_id):
        return {
        "success": False,
        "error": "Invalid customer ID format. Expected CUS-XXXXX.",
    }

    if not action_type.strip():
        return {
            "success": False,
            "error": "action_type cannot be empty.",
        }

    if not performed_by.strip():
        return {
            "success": False,
            "error": "performed_by cannot be empty.",
        }

    if not customer_id.strip():
        return {
            "success": False,
            "error": "customer_id cannot be empty.",
        }

    if not outcome.strip():
        return {
            "success": False,
            "error": "outcome cannot be empty.",
        }

    customer = get_customer(customer_id)

    if not customer:
        return {
            "success": False,
            "error": f"Customer not found: {customer_id}",
        }

    audit_entry = write_audit_log(
        timestamp=datetime.now().isoformat(),
        action_type=action_type.strip(),
        performed_by=performed_by.strip(),
        customer_id=customer_id.strip(),
        outcome=outcome.strip(),
    )

    return {
        "success": True,
        "audit_log": audit_entry,
    }