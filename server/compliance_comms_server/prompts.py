def transaction_analysis_prompt(
    customer_name: str,
    account_type: str,
    analysis_period: str,
) -> str:
    """
    MCP Prompt:
        transaction_analysis_prompt
    """

    return f"""
Analyze the transactions for the following customer.

Customer Name: {customer_name}
Account Type: {account_type}
Analysis Period: {analysis_period}

Provide a concise analysis covering:
1. Total transaction activity
2. Unusual or potentially suspicious patterns
3. Significant amounts or frequency changes
4. Any observations that may require further compliance review

Do not assume facts that are not present in the transaction data.
Clearly distinguish observed information from potential concerns.
""".strip()

def build_transaction_analysis_prompt(
    customer_name: str,
    account_type: str,
    analysis_period: str,
) -> str:
    return f"""
Analyze the transactions for the following customer.

Customer Name: {customer_name}
Account Type: {account_type}
Analysis Period: {analysis_period}

Provide:
1. Summary of transaction activity
2. Unusual or suspicious patterns
3. Potential risks
4. Recommended next actions
""".strip()


def customer_communication_prompt(
    template_name: str,
    customer_name: str,
    account_tier: str,
    specific_detail: str,
) -> str:
    """
    MCP Prompt:
        customer_communication_prompt
    """

    return f"""
Prepare a customer communication using the following details.

Template: {template_name}
Customer Name: {customer_name}
Account Tier: {account_tier}
Specific Detail: {specific_detail}

Requirements:
1. Use the specified communication template.
2. Keep the message clear and professional.
3. Address the customer appropriately.
4. Include only the provided details.
5. Do not invent customer information.
6. Do not expose unnecessary sensitive information.
""".strip()

def build_customer_communication_prompt(
    template_name: str,
    customer_name: str,
    account_tier: str,
    specific_detail: str,
) -> str:
    return f"""
Prepare a customer communication using the template "{template_name}".

Customer Name: {customer_name}
Customer Tier: {account_tier}
Details: {specific_detail}

The communication should be clear, professional, concise, and appropriate
for the customer's situation.
""".strip()