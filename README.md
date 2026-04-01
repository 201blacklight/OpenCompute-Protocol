# OpenCompute Protocol MVP (Engineering-Core)

可运行 MVP，覆盖：
- 统一计量：`Quote` 和 `Consume`
- 路由：按 `providerId` 路由，未知提供方降级到 `mock`
- 账单：`Reconcile` 生成对账结果
- 权限：API Key + 简单 RBAC
- 审计：`Audit` 查询事件链

## 最小接口集

- `POST /api/v1/quote`
- `POST /api/v1/consume`
- `POST /api/v1/reconcile`
- `GET /api/v1/audit-trail`
- `GET /healthz`

## 快速启动

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

## 测试

```bash
pytest -q
```

## Provider 适配

当前已接入（先易后难）：
- `mock`（本地稳定）
- `openai`（静态报价适配）
- `anthropic`（模拟瞬时失败 + 重试）

## 鉴权示例

Header:
- `X-API-Key: mvp-admin-key`（全接口）
- `X-API-Key: mvp-ops-key`（除审计外）
- `X-API-Key: mvp-auditor-key`（仅审计）

## 幂等与重试

- `consume/reconcile` 支持 `Idempotency-Key`
- Provider 报价调用实现 3 次重试（超时场景）

## 正式仓库结构

```text
OpenCompute Protocol/
├─ app/                         # 现有 API MVP
├─ tests/                       # 现有 API 测试
├─ docs/
│  ├─ decision/                 # 决策层策略文档
│  ├─ architecture/iterations/  # 架构迭代与审计文档
│  └─ governance/               # Agent 分工、MCP 配置、交付规范
├─ demo/
│  └─ ocp_demo/                 # Token 结算演示代码（可运行）
└─ scripts/                     # 一键运行脚本
```

## OCP Demo（策略-架构-执行闭环样例）

- Demo 路径：`demo/ocp_demo`
- 目标：演示“支付回执 -> Token发放 -> 模型扣费 -> 收益分成/转移 -> 争议冻结”
- 运行：

```bash
python demo/ocp_demo/main.py
python -m pytest demo/ocp_demo/tests/test_engine.py -q
```

## 开源协作

- 贡献指南：`CONTRIBUTING.md`
- PR 模板：`.github/PULL_REQUEST_TEMPLATE.md`
- Issue 模板：`.github/ISSUE_TEMPLATE/`
