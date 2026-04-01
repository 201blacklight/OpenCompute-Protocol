# OCP 架构 v2（审计通过）

## 关键增强
- 增加账本状态机：冻结、解冻、冲正、争议。
- 对所有回执驱动转换增加幂等、nonce、签名校验。
- 增加双分录风格事件，提升追溯能力。
- 增加监管与试点报表接口。
- 增加沙箱 SDK，降低企业接入门槛。

## 账本状态
- `INIT -> PENDING_RECEIPT`
- `PENDING_RECEIPT -> CREDITED | REJECTED`
- `CREDITED -> RESERVED -> CONSUMED`
- `RESERVED -> RELEASED`
- `CONSUMED -> REFUND_PENDING -> REFUNDED`
- `* -> DISPUTED -> RESOLVED`

## 验收结论
- 在“非托管资金”边界内，准许进入 Demo 实施阶段。
