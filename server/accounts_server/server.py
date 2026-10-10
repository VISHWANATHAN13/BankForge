from fastmcp import FastMCP

from server.accounts_server.tools import (
    get_account_summary_tool,
    get_accounts_for_customer_tool,
    get_transaction_history_tool,
)
from server.accounts_server.resources import (
    get_account_summary_resource,
)


mcp = FastMCP("BankForge Accounts Server")


@mcp.tool()
def get_account_summary(account_id: str):
    return get_account_summary_tool(account_id)


@mcp.tool()
def get_accounts_for_customer(customer_id: str):
    return get_accounts_for_customer_tool(customer_id)


@mcp.tool()
def get_transaction_history(
    account_id: str,
    limit: int = 10,
):
    return get_transaction_history_tool(
        account_id=account_id,
        limit=limit,
    )

@mcp.resource("account://{account_id}/summary")
def account_summary_resource(account_id: str):
    return get_account_summary_resource(account_id)

if __name__ == "__main__":
    mcp.run()