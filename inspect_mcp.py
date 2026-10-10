import asyncio

from server.accounts_server.server import mcp as accounts_mcp
from server.products_server.server import mcp as products_mcp
from server.compliance_comms_server.server import mcp as compliance_mcp


async def inspect_server(name, mcp):
    tools = await mcp.list_tools()
    resources = await mcp.list_resources()
    templates = await mcp.list_resource_templates()
    prompts = await mcp.list_prompts()

    print("=" * 70)
    print(name)
    print("=" * 70)

    print(f"\nTOOLS ({len(tools)})")
    for tool in tools:
        print(f"  - {tool.name}")

    print(f"\nRESOURCES ({len(resources)})")
    for resource in resources:
        print(f"  - {resource.uri}")

    print(f"\nRESOURCE TEMPLATES ({len(templates)})")
    for template in templates:
        print(f"  - {template.uri_template}")

    print(f"\nPROMPTS ({len(prompts)})")
    for prompt in prompts:
        print(f"  - {prompt.name}")

    return len(tools), len(resources), len(templates), len(prompts)


async def main():
    accounts = await inspect_server(
        "BANKFORGE ACCOUNTS SERVER",
        accounts_mcp,
    )

    products = await inspect_server(
        "BANKFORGE PRODUCTS SERVER",
        products_mcp,
    )

    compliance = await inspect_server(
        "BANKFORGE COMPLIANCE & COMMUNICATIONS SERVER",
        compliance_mcp,
    )

    total_tools = accounts[0] + products[0] + compliance[0]
    total_resources = accounts[1] + products[1] + compliance[1]
    total_templates = accounts[2] + products[2] + compliance[2]
    total_prompts = accounts[3] + products[3] + compliance[3]

    print("\n" + "=" * 70)
    print("BANKFORGE MCP ECOSYSTEM SUMMARY")
    print("=" * 70)

    print(f"Tools:              {total_tools}")
    print(f"Resources:          {total_resources}")
    print(f"Resource Templates: {total_templates}")
    print(f"Prompts:            {total_prompts}")

    print("\nExpected:")
    print("Tools:              14")
    print("Resources:          0")
    print("Resource Templates: 4")
    print("Prompts:            2")


if __name__ == "__main__":
    asyncio.run(main())