from data.products.database import get_loan_product
from common.guardrails import validate_product_id

def get_product_details_resource(product_id: str):
    """
    MCP Resource:
        product://{product_id}/details
    """
    if not validate_product_id(product_id):
        return {
        "error": "Invalid product ID format. Expected PROD-XX-XX."
    }

    product = get_loan_product(product_id)

    if not product:
        return {
            "error": f"Loan product not found: {product_id}"
        }

    return product