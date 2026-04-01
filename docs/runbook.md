# 运行手册

## 1. 服务启动

- 命令：`uvicorn app.main:app --host 0.0.0.0 --port 8080`
- 健康检查：`GET /healthz`
- 日志关键字：
  - `quote.start / quote.done`
  - `consume.start / consume.done / consume.idempotent_hit`
  - `reconcile.start / reconcile.done / reconcile.idempotent_hit`
  - `audit.query`

## 2. 核心接口调用顺序

1) `POST /api/v1/quote`
2) `POST /api/v1/consume`（带 `Idempotency-Key`）
3) `POST /api/v1/reconcile`（带 `Idempotency-Key`）
4) `GET /api/v1/audit-trail?traceId=...`

## 3. 值班检查项

- 5xx 比例
- provider 重试次数（超阈值告警）
- `idempotent_hit` 比例（异常突增需排查重复请求来源）
- reconcile 的 `MISMATCH` 比例

## 4. 手工恢复动作

- 重放请求：使用原始 `Idempotency-Key`，确保不重复记账
- 对账补偿：对 `MISMATCH` 发起人工复核和补单
- 审计追踪：通过 `traceId` 抽取完整事件链
