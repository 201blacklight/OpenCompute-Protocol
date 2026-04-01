# 部署文档（本地/云）

## 1. 本地部署

1) 准备 Python 3.10+
2) 安装依赖
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
```
3) 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```
4) 健康检查：`GET /healthz`

## 2. 容器化部署

示例 Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

构建与运行：
```bash
docker build -t opencompute-mvp:0.1.0 .
docker run -p 8080:8080 opencompute-mvp:0.1.0
```

## 3. 云上部署建议

- **K8s**：Deployment + Service + HPA（按 QPS/CPU）
- **配置注入**：将 API Key/角色映射迁移至 Secret/ConfigMap
- **日志**：对接 ELK 或 Loki，按 `request_id` 可追踪
- **可用性**：建议最少 2 副本，滚动升级

## 4. 发布检查清单

- `pytest -q` 全绿
- `/healthz` 正常
- 四个核心接口冒烟通过
- 审计链路（quote -> audit）可复现
