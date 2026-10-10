# BankForge 

A lightweight demonstration suite for the BankForge MCP (Modular Connector Platform) ecosystem — includes runtime validators, inspection utilities, communication templates, and example servers used for testing and demos.

## Overview

BankForge provides a small, opinionated reference implementation of an MCP-based banking demo. It contains example servers for Accounts, Products, and Compliance/Communications along with tools to inspect the MCP surface, validate runtime behaviour, and exercise tools, prompts, resources, and templates.

## Key Features

- Runtime validators for resources, prompts, and tools
- MCP inspection utilities to enumerate tools/resources/prompts
- Example communication templates for customer interactions
- Basic audit and guardrail helpers under `common`
- Tests to validate behavior and examples

## Quick Start

1. Create a virtual environment and activate it (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Inspect the MCP servers (lists tools, resources, templates, prompts):

```powershell
python inspect_mcp.py
```

4. Run runtime validations for resources and prompts:

```powershell
python runtime_mcp.py
```

5. Run tool validations that exercise the MCP tool surface:

```powershell
python runtime_tools.py
```

## Project Structure

- [inspect_mcp.py](2531814-BankForge/inspect_mcp.py) — Inspect servers and enumerate tools/resources/prompts
- [runtime_mcp.py](2531814-BankForge/runtime_mcp.py) — Validate resource and prompt runtime behavior
- [runtime_tools.py](2531814-BankForge/runtime_tools.py) — Execute and validate MCP tools
- [requirements.txt](2531814-BankForge/requirements.txt) — Python dependencies
- [common](2531814-BankForge/common/) — Shared helpers (guardrails, audit, logging)
- [communication_templates](2531814-BankForge/communication_templates/) — Markdown templates used by prompts/tools
- [tests](2531814-BankForge/tests/) — Pytest test suite for key behaviors
- [docker](2531814-BankForge/docker/) — Docker artifacts (example server containers)

## Usage Notes

- The runtime scripts call into example `server` packages (Accounts, Products, Compliance/Communications). Ensure any expected backing services or in-repo mock servers are reachable when running the validators.
- The project is designed as a demo/testbed. Some runtime tests may create or depend on seeded data (see `runtime_tools.py` and `runtime_mcp.py` for example IDs like `ACC-00001`, `APP-00001`).

## Testing

Run the test suite with pytest:

```powershell
pytest -q
```

## Contributing

Contributions welcome. Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Keep changes small and focused
4. Add tests where appropriate
5. Open a PR and reference the behavior you changed

## License

This repository does not include a license file. Add a `LICENSE` to define reuse permissions.

