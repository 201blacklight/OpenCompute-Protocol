# OCP 架构 v1 提案

## 分层组件
- Gateway + Auth
- Token Exchange + Pricing
- Payment Receipt + Settlement
- Usage Ledger + Revenue Share Registry
- Payment/Model Adapters
- Audit + Risk

## 核心流程
1. 外部支付完成。
2. 支付回执入站并校验。
3. 根据汇率策略发放 Token 额度。
4. 模型调用后扣减 Token。
5. 收益按当前受益人规则入账。

## v1 已知缺口
- 缺少反操纵的汇率控制机制。
- 部分失败场景下的对账状态不完整。
- 分成权转移的争议处理偏弱。
