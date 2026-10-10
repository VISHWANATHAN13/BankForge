from fastmcp import FastMCP

from server.products_server.tools import (
    list_loan_products_tool,
    get_loan_product_details_tool,
    check_eligibility_criteria_tool,
)
from server.products_server.tools import (
    list_loan_products_tool,
    get_loan_product_details_tool,
    check_eligibility_criteria_tool,
    submit_loan_application_tool,
    get_loan_application_status_tool,
)

from server.products_server.resources import (
    get_product_details_resource,
)


mcp = FastMCP("BankForge Products Server")


@mcp.tool(name="list_loan_products")
def list_loan_products(category: str | None = None):
    return list_loan_products_tool(category)


@mcp.tool(name="get_loan_product_details")
def get_loan_product_details(product_id: str):
    return get_loan_product_details_tool(product_id)


@mcp.tool(name="check_eligibility_criteria")
def check_eligibility_criteria(
    product_id: str,
    applicant_risk_rating: str,
):
    return check_eligibility_criteria_tool(
        product_id,
        applicant_risk_rating,
    )

@mcp.tool(name="submit_loan_application")
def submit_loan_application(
    customer_id: str,
    product_id: str,
    requested_amount: float,
):
    return submit_loan_application_tool(
        customer_id,
        product_id,
        requested_amount,
    )


@mcp.tool(name="get_loan_application_status")
def get_loan_application_status(
    application_id: str,
):
    return get_loan_application_status_tool(
        application_id,
    )

@mcp.resource("product://{product_id}/details")
def product_details_resource(product_id: str):
    return get_product_details_resource(product_id)


if __name__ == "__main__":
    mcp.run()