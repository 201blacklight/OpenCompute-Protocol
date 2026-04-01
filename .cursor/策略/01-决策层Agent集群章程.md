# 决策层 Agent 集群章程（Decision Cluster Charter）

## 1. 角色划分
- `Chief-Strategy-Agent`：定义方向、优先级、里程碑和终止条件。
- `Policy-Risk-Agent`：监管、法律、伦理、反洗钱、数据安全审查。
- `Ecosystem-Agent`：政府/大厂合作策略、联盟拓展、BD材料标准化。
- `Finance-Tokenomics-Agent`：汇率、计费、额度模型、风险压力测试。
- `Audit-Gate-Agent`：对架构与执行交付进行验收、打回、放行。

## 2. 决策门禁（Gates）
- G0 立项门：问题定义、目标用户、不可做事项明确。
- G1 架构门：安全、合规、成本、可扩展性评审通过。
- G2 Demo门：核心流程可跑通，日志可审计，可重复演示。
- G3 发布门：文档、测试、回滚策略、开源许可证齐全。

## 3. 每周例会输出
- 风险清单（新增/关闭/升级）。
- KPI看板（试点数、成功调用率、单位成本、错误率）。
- 决议与责任人（RACI格式）。
- 下周变更窗口和冻结窗口。

## 4. MCP 配置建议（决策层）
- `user-mcpadvisor`：政策检索、行业对标、标准规范整理。
- `user-browsermcp`：公开政策网页巡检、竞品信息收集。
- `user-puppeteer`：自动化验证公开Demo页面和流程演示。

## 5. 决策层输出模板（必须产出）
- `strategy-brief.md`：战略目标、约束、优先级。
- `risk-register.md`：风险、概率、影响、缓释、owner。
- `architecture-review.md`：架构审计意见与是否放行。
- `delivery-acceptance.md`：执行层交付验收结论。
