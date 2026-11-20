# MCP capability discovery; example remains DISABLED by default

MCP belongs in the initial capability inventory alongside OpenCode agents and skills. Use a connected, approved MCP tool when it provides relevant structured access to an internal system (for example, Git queries, database schemas, or authorized Prometheus/Grafana/Splunk queries). A local CLI may be better for a particular operation; make that choice after comparing the same task and acceptance criteria. Agentic reasoning, skills, MCP service calls, and deterministic CLI execution can be composed in one workflow.

This example stays disabled by default because the server, SDK, permissions, internal compatibility, and offline behavior are not qualified here. Discover and test already-approved integrations; do not install or enable this example until it has passed qualification. Neither a generic internet MCP gateway nor a mandatory background server is part of Golden Core.

Public OpenCode V2 example shape, **not tested against your internal build**:

```json
{
  "mcp": {
    "servers": {
      "company-authorized-data": {
        "type": "local",
        "command": ["python", "-m", "company_approved_mcp_server"],
        "disabled": true
      }
    }
  }
}
```

Do not copy this into your real config until the server implementation, Python SDK, dependencies, service endpoints, token handling, permissions, security review and Windows/Linux compatibility have been qualified. Keep it `disabled: true` until authorized. Do not assume every OpenCode version uses the same MCP config structure. Runtime public internet is not allowed.

Official docs: https://opencode.ai/docs/mcp-servers/
