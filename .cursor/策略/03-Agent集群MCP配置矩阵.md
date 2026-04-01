# Agent 集群 MCP 配置矩阵

## 决策层 Agent 集群
- 主要目标：政策研判、战略审计、验收决策。
- MCP建议：
  - `user-mcpadvisor`：政策和行业规则分析（主用）。
  - `user-browsermcp`：公开网页信息验证（辅助）。
  - `user-puppeteer`：自动回归演示页面（辅助）。

## 架构设计 Agent 集群
- 主要目标：协议设计、安全设计、可扩展架构输出。
- MCP建议：
  - `user-mcpadvisor`：标准协议参考与最佳实践。
  - `user-browsermcp`：查阅开放API/SDK文档。
  - `user-puppeteer`：验证SDK文档示例可操作性。

## 执行层 Agent 集群
- 主要目标：编码、测试、演示、交付打包。
- MCP建议：
  - `user-puppeteer`：自动化Demo验收流程。
  - `user-browsermcp`：前端/页面化Demo联调验证。
  - `user-mcpadvisor`：发布规范与交付建议。

## 配置原则
- 最小权限：每类Agent只启用必要MCP。
- 可审计：所有关键动作写入审计记录。
- 可降级：任一MCP不可用时，支持本地离线流程。
