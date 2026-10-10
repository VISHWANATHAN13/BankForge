from pathlib import Path

import data.products.database as products_db

from server.products_server.tools import (
    list_loan_products_tool,
    get_loan_product_details_tool,
    check_eligibility_criteria_tool,
    submit_loan_application_tool,
    get_loan_application_status_tool,
)


def setup_module():
    products_db.init_db(force=True)


def test_list_loan_products():
    result = list_loan_products_tool()

    assert result["success"] is True
    assert result["count"] > 0


def test_get_loan_product_details():
    result = get_loan_product_details_tool("PROD-LN-01")

    assert result["success"] is True
    assert result["product"]["product_id"] == "PROD-LN-01"


def test_invalid_product():
    result = get_loan_product_details_tool("PROD-LN-99")

    assert result["success"] is False


def test_eligibility():
    result = check_eligibility_criteria_tool(
        "PROD-LN-01",
        "LOW",
    )

    assert result["success"] is True
    assert "eligible" in result


def test_kyc_gate():
    result = submit_loan_application_tool(
    customer_id="CUS-00003",
    product_id="PROD-LN-01",
    requested_amount=200000,
)

    assert result["success"] is False
    assert "KYC" in result["error"]


def test_submit_loan_application():
    result = submit_loan_application_tool(
        customer_id="CUS-00001",
        product_id="PROD-LN-01",
        requested_amount=100000,
    )
    print(result)

    assert result["success"] is True

    application_id = result["application"]["application_id"]

    status = get_loan_application_status_tool(application_id)

    assert status["success"] is True
    assert status["application"]["status"] == "PENDING"