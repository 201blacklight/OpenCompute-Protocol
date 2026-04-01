# Contributing Guide

Thanks for contributing to OpenCompute Protocol.

## Quick Start

1. Fork and clone the repository.
2. Create a feature branch from `main`.
3. Install dependencies:
   - `pip install -e ".[dev]"`
4. Run checks before opening a PR:
   - `pytest -q`
   - `python demo/ocp_demo/main.py`

## Branch and Commit Conventions

- Branch naming:
  - `feat/<short-description>`
  - `fix/<short-description>`
  - `docs/<short-description>`
- Commit style (recommended):
  - `feat: ...`
  - `fix: ...`
  - `docs: ...`
  - `test: ...`
  - `chore: ...`

## Pull Request Requirements

- Keep PRs focused and reasonably small.
- Include problem statement, design notes, and test evidence.
- Update docs for behavior, API, or architecture changes.
- Add tests for new logic and bug fixes.

## Documentation Policy

- Bilingual docs live in:
  - `docs/zh/` (Chinese)
  - `docs/en/` (English)
- For major changes, update both languages in the same PR.

## Security and Compliance Notes

- Do not commit secrets, keys, or private credentials.
- Do not add direct fund-custody logic without explicit governance approval.
- Keep receipt-driven accounting boundaries clear and auditable.
