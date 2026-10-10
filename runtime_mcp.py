import asyncio

from server.accounts_server.server import mcp as accounts_mcp
from server.products_server.server import mcp as products_mcp
from server.compliance_comms_server.server import mcp as compliance_mcp


async def test_resource(mcp, uri, label):
    print(f"\n[RESOURCE] {label}")
    try:
        result = await mcp.read_resource(uri)
        print("  PASS")
        print(f"  {result}")
    except Exception as e:
        print("  FAIL")
        print(f"  {type(e).__name__}: {e}")

async def test_prompt(mcp, name, arguments, label):
    print(f"\n[PROMPT] {label}")
    try:
        result = await mcp.get_prompt(
            name,
            arguments,
        )
        print("  PASS")
        print(f"  {result}")
    except Exception as e:
        print("  FAIL")
        print(f"  {type(e).__name__}: {e}")

async def main():

    print("=" * 70)
    print("BANKFORGE MCP RUNTIME VALIDATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # ACCOUNTS RESOURCE
    # ---------------------------------------------------------

    await test_resource(
        accounts_mcp,
        "account://ACC-00001/summary",
        "Account Summary",
    )

    # ---------------------------------------------------------
    # PRODUCTS RESOURCE
    # ---------------------------------------------------------

    await test_resource(
        products_mcp,
        "product://PROD-LN-01/details",
        "Loan Product Details",
    )

    # ---------------------------------------------------------
    # COMPLIANCE RESOURCES
    # ---------------------------------------------------------

    await test_resource(
        compliance_mcp,
        "customer://CUS-00001/profile",
        "Customer Profile",
    )

    await test_resource(
        compliance_mcp,
        "template://loan_approval.md",
        "Communication Template",
    )

    # ---------------------------------------------------------
    # PROMPTS
    # ---------------------------------------------------------

    await test_prompt(
        compliance_mcp,
        "transaction_analysis_prompt",
        {
            "customer_name": "Arjun Mehta",
            "account_type": "savings",
            "analysis_period": "last 30 days",
        },
        "Transaction Analysis Prompt",
    )

    await test_prompt(
        compliance_mcp,
        "customer_communication_prompt",
        {
            "template_name": "loan_approval.md",
            "customer_name": "Arjun Mehta",
            "account_tier": "PREMIUM",
            "specific_detail": "Loan application approved.",
        },
        "Customer Communication Prompt",
    )

    print("\n" + "=" * 70)
    print("RUNTIME VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())