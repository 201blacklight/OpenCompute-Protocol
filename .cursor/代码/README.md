# OCP Demo（执行层交付）

这个目录是最小可运行Demo，目标是证明以下闭环可实现：
- 支付回执触发Token发放
- Token支付AI调用费用
- 模型收益分成与分成权转移
- 争议状态下收益冻结
- 审计日志可追溯

## 目录
- `opencompute_demo.py`：核心逻辑与演示入口
- `test_opencompute_demo.py`：核心回归测试
- `run_demo.ps1`：Windows演示脚本
- `github-交付清单.md`：上传GitHub前检查项

## 运行
```powershell
cd ".cursor\代码"
python .\opencompute_demo.py
python -m pytest .\test_opencompute_demo.py -q
```

## 后续接入建议
- 将 `process_payment_receipt` 替换为真实支付回执验签流程。
- 将 `consume_model` 接到真实模型网关的调用计量事件。
- 将 `ledger` 改为数据库持久化 + append-only事件流。
