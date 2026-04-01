# Agent 集群与 MCP 矩阵

## 决策层集群
- 目标：战略、合规门禁、架构验收、交付验收。
- 推荐 MCP：
  - `user-mcpadvisor`（政策与标准分析主用）
  - `user-browsermcp`（公开信息校验）
  - `user-puppeteer`（Demo 流程验证）

## 架构层集群
- 目标：协议、安全、可靠性、数据模型演进。
- 推荐 MCP：
  - `user-mcpadvisor`（标准与实践）
  - `user-browsermcp`（外部 API/规范参考）
  - `user-puppeteer`（SDK 流程验证）

## 执行层集群
- 目标：编码、测试、打包、交付。
- 推荐 MCP：
  - `user-puppeteer`（自动化验收）
  - `user-browsermcp`（UI/文档校验）
  - `user-mcpadvisor`（发布检查建议）
