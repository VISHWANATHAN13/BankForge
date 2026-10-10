from data.accounts.database import get_account
from common.guardrails import validate_account_id

def get_account_summary_resource(account_id: str):
    """
    MCP Resource:
        account://{account_id}/summary
    """
    if not validate_account_id(account_id):
        return {
            "error": "Invalid account ID format. Expected ACC-XXXXX."
        }

    account = get_account(account_id)

    if not account:
        return {
            "error": f"Account not found: {account_id}"
        }

    return {
        "account_id": account["account_id"],
        "account_type": account["account_type"],
        "balance": account["balance"],
        "status": account["status"],
    }