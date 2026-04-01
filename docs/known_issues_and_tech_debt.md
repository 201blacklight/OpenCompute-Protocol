# 已知问题与技术债清单

## 已知问题

1. 当前存储为内存态，服务重启后数据丢失。
2. API Key 与权限映射硬编码，不适合生产。
3. Provider 适配为最小化实现，尚未接入真实 SDK 与签名校验。
4. Reconcile 逻辑使用简化算法（基于摘要偏差模拟），非正式财务算法。

## 技术债

1. 引入持久化数据库（PostgreSQL）与事务账本表。
2. 为幂等存储增加 TTL、冲突检测与多节点一致性方案（Redis）。
3. 增强可观测性（OpenTelemetry trace + metrics + SLO）。
4. 增加契约测试（基于 OpenAPI）与 provider 沙箱回归测试。
5. 补齐 CI/CD（lint/type/test/security scan）与灰度发布流水线。
