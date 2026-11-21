# MCP capability discovery; synthetic fixture remains DISABLED by default

MCP belongs in the initial capability inventory alongside OpenCode agents and skills. Use a connected, approved MCP tool when it provides relevant structured access to an internal system (for example, Git queries, database schemas, or authorized Prometheus/Grafana/Splunk queries). A local CLI may be better for a particular operation; make that choice after comparing the same task and acceptance criteria. Agentic reasoning, skills, MCP service calls, and deterministic CLI execution can be composed in one workflow.

`synthetic_fixture.py` provides one fixed, read-only synthetic sample over local JSON-RPC stdio, and the unit tests exercise discovery, call scope, errors, cancellation/timeout cases and prompt-injection-shaped fixture data. It is a test fixture, not a general MCP implementation or a qualified server. Cancellation and timeout are contract cases in the direct handler; the stdio loop does not cancel a running request. The MCP Python SDK is not staged in this repository, and this fixture has not been connected to company OpenCode. Discover and test already-approved integrations; do not enable it in a company configuration until the approved staged SDK and actual internal client pass qualification.

The repo-local OpenCode V2 example entry is present in root `opencode.json` and `.opencode/opencode.json` with `disabled: true` and legacy protocol pinned. Neither config file is copied into a company config by bootstrap. Runtime public internet is not allowed. OpenCode's public V2 docs define local servers as stdio commands and use `disabled: true`; verify against the internal build before adopting that shape: https://opencode.ai/docs/mcp-servers/.

## GitHub Enterprise read-only candidate

[`github-enterprise-readonly.example.json`](github-enterprise-readonly.example.json) is a disabled configuration example for GitHub's official local MCP server v2.2.0. It targets only an approved **internal GitHub Enterprise Server** host, selects repository/issue/pull-request/Actions toolsets, and sets upstream `--read-only`. It does not use GitHub's remote MCP service, GitHub.com, GitHub Enterprise Cloud, or an online container image. The `.invalid` hostname is a placeholder; place the approved per-platform `github-mcp-server` executable on the managed `PATH` only after staging and review.

The template reads `GITHUB_PERSONAL_ACCESS_TOKEN` from the OpenCode process environment through OpenCode's `{env:NAME}` substitution. Put that value in the company's approved credential mechanism, never in this repository or a committed OpenCode config. Server read-only mode hides write tools but does not replace least-privilege PAT permissions, GHES authorization, or default-deny network controls. Keep the server disabled until the internal OpenCode schema/build, staged binary/module/SBOM/license package, GHES endpoint, token handling, permission scope, and Windows/Linux behavior have passed company review. This is an evaluation template, not an enabled or approved integration.

For local code edits and commits, keep using the existing Git workflow. Compare the MCP with another path only for a matching remote task such as reading issue/PR/Actions context, using the same acceptance criteria. The server's GitHub API audit entries are not by themselves proof that a specific OpenCode MCP tool was invoked.

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
