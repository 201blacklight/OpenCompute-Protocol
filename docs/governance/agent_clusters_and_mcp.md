# Agent Clusters and MCP Matrix

## Decision Cluster
- Goals: strategy, compliance gate, architecture acceptance, delivery acceptance.
- Recommended MCPs:
  - `user-mcpadvisor` (primary policy/standards analysis)
  - `user-browsermcp` (public information validation)
  - `user-puppeteer` (demo flow validation)

## Architecture Cluster
- Goals: protocol, security, reliability, data model evolution.
- Recommended MCPs:
  - `user-mcpadvisor` for standards and patterns
  - `user-browsermcp` for external API/spec references
  - `user-puppeteer` for SDK walkthrough verification

## Execution Cluster
- Goals: build, test, package, handoff.
- Recommended MCPs:
  - `user-puppeteer` for automated acceptance flows
  - `user-browsermcp` for UI or docs validation
  - `user-mcpadvisor` for release checklists
