# OCP Settlement Demo

## Purpose
- Demonstrate a minimal, auditable lifecycle:
  - payment receipt -> token minting
  - model consumption -> token deduction
  - revenue share transfer
  - dispute freeze behavior

## Run
```bash
python demo/ocp_demo/main.py
python -m pytest demo/ocp_demo/tests/test_engine.py -q
```

## Visual Preview

```bash
python demo/ocp_demo/visual_preview.py
```

This mode prints step-by-step account deltas, snapshots, and an event timeline.
