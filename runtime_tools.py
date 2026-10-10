import asyncio

from server.accounts_server.server import mcp as accounts_mcp
from server.products_server.server import mcp as products_mcp
from server.compliance_comms_server.server import mcp as compliance_mcp


async def test_tool(mcp, name, arguments, label):
    print(f"\n[TOOL] {label}")

    try:
        result = await mcp.call_tool(
            name,
            arguments,
        )

        print("  PASS")
        print(f"  {result}")

        return True

    except Exception as e:
        print("  FAIL")
        print(f"  {type(e).__name__}: {e}")

        return False


async def main():

    passed = 0
    total = 14

    print("=" * 70)
    print("BANKFORGE MCP TOOL RUNTIME VALIDATION")
    print("=" * 70)

    # =========================================================
    # ACCOUNTS SERVER
    # =========================================================

    if await test_tool(
        accounts_mcp,
        "get_account_summary",
        {
            "account_id": "ACC-00001",
        },
        "Get Account Summary",
    ):
        passed += 1

    if await test_tool(
        accounts_mcp,
        "get_accounts_for_customer",
        {
            "customer_id": "CUS-00001",
        },
        "Get Accounts For Customer",
    ):
        passed += 1

    if await test_tool(
        accounts_mcp,
        "get_transaction_history",
        {
            "account_id": "ACC-00001",
            "limit": 10,
        },
        "Get Transaction History",
    ):
        passed += 1

    # =========================================================
    # PRODUCTS SERVER
    # =========================================================

    if await test_tool(
        products_mcp,
        "list_loan_products",
        {},
        "List Loan Products",
    ):
        passed += 1

    if await test_tool(
        products_mcp,
        "get_loan_product_details",
        {
            "product_id": "PROD-LN-01",
        },
        "Get Loan Product Details",
    ):
        passed += 1

    if await test_tool(
        products_mcp,
        "check_eligibility_criteria",
        {
            "product_id": "PROD-LN-01",
            "applicant_risk_rating": "LOW",
        },
        "Check Eligibility Criteria",
    ):
        passed += 1

    # This creates one real application.
    if await test_tool(
        products_mcp,
        "submit_loan_application",
        {
            "customer_id": "CUS-00001",
            "product_id": "PROD-LN-01",
            "requested_amount": 100000,
        },
        "Submit Loan Application",
    ):
        passed += 1

    # Use the known seeded application so this does not depend
    # on the newly created application ID.
    if await test_tool(
        products_mcp,
        "get_loan_application_status",
        {
            "application_id": "APP-00001",
        },
        "Get Loan Application Status",
    ):
        passed += 1

    # =========================================================
    # COMPLIANCE & COMMUNICATIONS SERVER
    # =========================================================

    if await test_tool(
        compliance_mcp,
        "get_kyc_status",
        {
            "customer_id": "CUS-00001",
        },
        "Get KYC Status",
    ):
        passed += 1

    if await test_tool(
        compliance_mcp,
        "run_compliance_check",
        {
            "customer_id": "CUS-00001",
        },
        "Run Compliance Check",
    ):
        passed += 1

    if await test_tool(
        compliance_mcp,
        "get_fraud_flags",
        {
            "customer_id": "CUS-00001",
        },
        "Get Fraud Flags",
    ):
        passed += 1

    if await test_tool(
        compliance_mcp,
        "generate_customer_communication",
        {
            "template_name": "loan_rejection.md",
            "customer_name": "Arjun Mehta",
            "account_tier": "PREMIUM",
            "specific_detail": "Application requires additional review.",
        },
        "Generate Customer Communication",
    ):
        passed += 1

    if await test_tool(
        compliance_mcp,
        "send_customer_communication",
        {
            "customer_id": "CUS-00001",
            "channel": "EMAIL",
            "message": "This is a runtime MCP validation message.",
        },
        "Send Customer Communication",
    ):
        passed += 1

    if await test_tool(
        compliance_mcp,
        "write_audit_log",
        {
            "action_type": "MCP_RUNTIME_TEST",
            "performed_by": "MCP_RUNTIME_VALIDATION",
            "customer_id": "CUS-00001",
            "outcome": "SUCCESS",
        },
        "Write Audit Log",
    ):
        passed += 1

    print("\n" + "=" * 70)
    print("BANKFORGE MCP TOOL VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\nALL 14 MCP TOOLS PASSED")
    else:
        print("\nSOME MCP TOOLS FAILED")


if __name__ == "__main__":
    asyncio.run(main())