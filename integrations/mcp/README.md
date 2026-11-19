# Optional MCP, DISABLED by default

CLI/skill first. Golden should attach a local MCP server only when a concrete task needs structured access to an approved internal system (read-only Git query, internal DB schema, Prometheus/Grafana/Splunk authorized query, etc.). Neither a generic internet MCP gateway nor a mandatory background server is part of Golden Core.

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
