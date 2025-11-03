# Contributing to OpenPrintKit

Thanks for your interest in contributing! This guide helps you get productive quickly.

## Local setup

- Python 3.11+
- Create a virtual environment and install dev extras:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -e '.[dev]'
  ```
- Run tests:
  ```bash
  PYTHONPATH=. pytest -q
  ```

## Linters / formatting

- Ruff (lint): `ruff check .`
- Black (format): `black .`
- CI runs both on push/PR (see `.github/workflows/lint.yml`).

## Pre-commit (recommended)

Install the hooks to keep docs synchronized and code tidy:
```bash
pip install pre-commit && pre-commit install
```
- Includes a local hook to regenerate `docs/exact-generator-keys.md` whenever generator modules change, failing if the doc is stale.

## Regenerating exact generator keys

If you modify `opk/plugins/slicers/*.py`, update the extracted keys:
```bash
python scripts/extract_generator_keys.py
```
This writes `docs/exact-generator-keys.md`. CI also checks this file is up to date.

## Docs

Docs are in `docs/` and published via GitHub Pages. To preview:
```bash
pip install -e '.[docs]'
mkdocs serve
```
The docs workflow regenerates exact keys before building.

## Releases

- See `docs/release-checklist.md` for the manual checklist.
- Tagged releases (`v*`) trigger `.github/workflows/release.yml` (build + PyPI publish with Trusted Publishing).

## Pull Requests

- Keep changes focused and accompanied by tests when applicable.
- For large changes, open an issue first to discuss goals and approach.

Thanks! 💙
