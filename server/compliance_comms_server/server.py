from fastmcp import FastMCP

from server.compliance_comms_server.prompts import (
    build_transaction_analysis_prompt,
    build_customer_communication_prompt,
)

from server.compliance_comms_server.tools import (
    get_kyc_status_tool,
    run_compliance_check_tool,
    get_fraud_flags_tool,
    generate_customer_communication_tool,
    send_customer_communication_tool,
)
from server.compliance_comms_server.tools import (
    get_kyc_status_tool,
    run_compliance_check_tool,
    get_fraud_flags_tool,
    generate_customer_communication_tool,
    send_customer_communication_tool,
    write_audit_log_tool,
)

from server.compliance_comms_server.resources import (
    get_customer_profile_resource,
    get_template_resource,
)

# from server.compliance_comms_server.prompts import (
#     transaction_analysis_prompt,
#     customer_communication_prompt,
# )

mcp = FastMCP("BankForge Compliance Communications Server")


@mcp.tool(name="get_kyc_status")
def get_kyc_status(customer_id: str):
    return get_kyc_status_tool(customer_id)


@mcp.tool(name="run_compliance_check")
def run_compliance_check(customer_id: str):
    return run_compliance_check_tool(customer_id)


@mcp.tool(name="get_fraud_flags")
def get_fraud_flags(customer_id: str):
    return get_fraud_flags_tool(customer_id)

@mcp.tool(name="generate_customer_communication")
def generate_customer_communication(
    template_name: str,
    customer_name: str,
    account_tier: str,
    specific_detail: str,
):
    return generate_customer_communication_tool(
        template_name,
        customer_name,
        account_tier,
        specific_detail,
    )


@mcp.tool(name="send_customer_communication")
def send_customer_communication(
    customer_id: str,
    channel: str,
    message: str,
):
    return send_customer_communication_tool(
        customer_id,
        channel,
        message,
    )

@mcp.tool(name="write_audit_log")
def write_audit_log(
    action_type: str,
    performed_by: str,
    customer_id: str,
    outcome: str,
):
    return write_audit_log_tool(
        action_type,
        performed_by,
        customer_id,
        outcome,
    )

@mcp.resource("customer://{customer_id}/profile")
def customer_profile_resource(customer_id: str):
    return get_customer_profile_resource(customer_id)


@mcp.resource("template://{template_name}")
def template_resource(template_name: str):
    return get_template_resource(template_name)

@mcp.prompt(name="transaction_analysis_prompt")
def transaction_analysis_prompt(
    customer_name: str,
    account_type: str,
    analysis_period: str,
) -> str:
    return build_transaction_analysis_prompt(
        customer_name,
        account_type,
        analysis_period,
    )


@mcp.prompt(name="customer_communication_prompt")
def customer_communication_prompt(
    template_name: str,
    customer_name: str,
    account_tier: str,
    specific_detail: str,
) -> str:
    return build_customer_communication_prompt(
        template_name,
        customer_name,
        account_tier,
        specific_detail,
    )

if __name__ == "__main__":
    mcp.run()