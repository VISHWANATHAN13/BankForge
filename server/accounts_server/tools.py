from data.accounts.database import (
    get_account,
    get_accounts_for_customer,
    get_transactions,
)
from common.guardrails import (
    validate_account_id,
    validate_customer_id,
    redact_for_logging,
)
from common.guardrails import (
    validate_account_id,
    validate_customer_id,
)
from common.logging_config import get_logger, trace
from common.guardrails import redact_for_logging

logger = get_logger(__name__)

@trace(logger, redact=redact_for_logging)
def get_account_summary_tool(account_id: str):
    if not validate_account_id(account_id):
        return {
            "success": False,
            "error": "Invalid account ID format. Expected ACC-XXXXX.",
        }

    account = get_account(account_id)

    if not account:
        return {
            "success": False,
            "error": f"Account not found: {account_id}",
        }

    return {
        "success": True,
        "account": {
            "account_id": account["account_id"],
            "account_type": account["account_type"],
            "balance": account["balance"],
            "status": account["status"],
        },
    }
@trace(logger, redact=redact_for_logging)
def get_accounts_for_customer_tool(customer_id: str):
    if not validate_customer_id(customer_id):
        return {
            "success": False,
            "error": "Invalid customer ID format. Expected CUS-XXXXX.",
        }

    accounts = get_accounts_for_customer(customer_id)

    safe_accounts = []

    for account in accounts:
        safe_accounts.append({
            "account_id": account["account_id"],
            "account_type": account["account_type"],
            "balance": account["balance"],
            "status": account["status"],
        })

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(safe_accounts),
        "accounts": safe_accounts,
    }
    
    
@trace(logger, redact=redact_for_logging)
def get_transaction_history_tool(
    account_id: str,
    limit: int = 10,
):
    if not validate_account_id(account_id):
        return {
            "success": False,
            "error": "Invalid account ID format. Expected ACC-XXXXX.",
        }

    if limit <= 0:
        return {
            "success": False,
            "error": "limit must be greater than zero.",
        }

    account = get_account(account_id)

    if not account:
        return {
            "success": False,
            "error": f"Account not found: {account_id}",
        }

    transactions = get_transactions(
        account_id=account_id,
        limit=limit,
    )

    return {
        "success": True,
        "account_id": account_id,
        "count": len(transactions),
        "transactions": transactions,
    }