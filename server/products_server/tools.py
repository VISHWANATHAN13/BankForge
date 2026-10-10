from typing import Optional

from data.products.database import (
    list_loan_products,
    get_loan_product,
)
from data.products.database import (
    list_loan_products,
    get_loan_product,
    create_loan_application,
    get_loan_application_status,
)
from common.guardrails import (
    validate_customer_id,
    validate_product_id,
    validate_application_id,
)
from common.logging_config import get_logger, trace
from common.guardrails import redact_for_logging

from data.compliance.database import is_kyc_verified

from common.audit import record_audit_event

logger = get_logger(__name__)

@trace(logger, redact=redact_for_logging)
def list_loan_products_tool(category: Optional[str] = None):
    """
    List available loan products.

    Args:
        category: Optional product category filter.

    Returns:
        List of loan products.
    """

    products = list_loan_products(category)

    return {
        "success": True,
        "count": len(products),
        "products": products,
    }

@trace(logger, redact=redact_for_logging)
def get_loan_product_details_tool(product_id: str):
    """
    Get details of a specific loan product.

    Args:
        product_id: Loan product ID.

    Returns:
        Loan product details or an error.
    """

    if not validate_product_id(product_id):
        return {
        "success": False,
        "error": "Invalid product ID format. Expected PROD-XX-XX.",
    }
    product = get_loan_product(product_id)
    
    if not product:
        return {
            "success": False,
            "error": f"Loan product not found: {product_id}",
        }

    return {
        "success": True,
        "product": product,
    }

@trace(logger, redact=redact_for_logging)
def check_eligibility_criteria_tool(
    product_id: str,
    applicant_risk_rating: str,
):
    """
    Check whether an applicant's risk rating satisfies
    the eligibility criteria for a loan product.

    Args:
        product_id: Loan product ID.
        applicant_risk_rating: Applicant risk rating.

    Returns:
        Eligibility result.
    """
    if not validate_product_id(product_id):
        return {
        "success": False,
        "error": "Invalid product ID format. Expected PROD-XX-XX.",
    }
    product = get_loan_product(product_id)

    if not product:
        return {
            "success": False,
            "error": f"Loan product not found: {product_id}",
        }

    required_rating = product["min_risk_rating"]

    eligible_ratings = {
        "LOW": 3,
        "MEDIUM": 2,
        "HIGH": 1,
    }

    applicant_score = eligible_ratings.get(
        applicant_risk_rating.upper()
    )

    required_score = eligible_ratings.get(
        required_rating.upper()
    )

    if applicant_score is None:
        return {
            "success": False,
            "error": f"Invalid risk rating: {applicant_risk_rating}",
        }

    if required_score is None:
        return {
            "success": False,
            "error": f"Invalid product risk requirement: {required_rating}",
        }

    eligible = applicant_score >= required_score

    return {
        "success": True,
        "eligible": eligible,
        "product_id": product_id,
        "applicant_risk_rating": applicant_risk_rating.upper(),
        "required_risk_rating": required_rating,
    }

@trace(logger, redact=redact_for_logging)
def submit_loan_application_tool(
    customer_id: str,
    product_id: str,
    requested_amount: float,
):
    if not validate_customer_id(customer_id):
        return {
            "success": False,
            "error": "Invalid customer ID format. Expected CUS-XXXXX.",
        }

    if not validate_product_id(product_id):
        return {
            "success": False,
            "error": "Invalid product ID format. Expected PROD-XX-XX.",
        }

    if requested_amount <= 0:
        return {
            "success": False,
            "error": "Requested amount must be greater than zero.",
        }

    if not is_kyc_verified(customer_id):
        record_audit_event(
        action_type="LOAN_APPLICATION_SUBMITTED",
        performed_by="MCP_CLIENT",
        customer_id=customer_id,
        outcome="REJECTED_KYC",
    )

        return {
        "success": False,
        "error": "Loan application rejected because KYC is not verified.",
        }

    product = get_loan_product(product_id)

    if not product:
        return {
            "success": False,
            "error": f"Loan product not found: {product_id}",
        }

    if not (
        product["min_amount"]
        <= requested_amount
        <= product["max_amount"]
    ):
        return {
            "success": False,
            "error": (
                f"Requested amount must be between "
                f"{product['min_amount']} and {product['max_amount']}."
            ),
        }

    application = create_loan_application(
        customer_id=customer_id,
        product_id=product_id,
        requested_amount=requested_amount,
    )
    record_audit_event(
    action_type="LOAN_APPLICATION_SUBMITTED",
    performed_by="MCP_CLIENT",
    customer_id=customer_id,
    outcome="SUCCESS",
    )

    return {
        "success": True,
        "application": application,
    }
    
@trace(logger, redact=redact_for_logging)
def get_loan_application_status_tool(
    application_id: str,
):
    """
    Retrieve the status of a loan application.
    """
    if not validate_application_id(application_id):
        return {
        "success": False,
        "error": "Invalid application ID format. Expected APP-XXXXX.",
    }

    application = get_loan_application_status(application_id)

    if not application:
        return {
            "success": False,
            "error": f"Loan application not found: {application_id}",
        }

    return {
        "success": True,
        "application": application,
    }