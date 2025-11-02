# OpenPrintKit — Release Checklist (Minimal)

Use this checklist to publish a new OPK release confidently.

## 1) Prep and sanity

- [ ] Ensure a clean working tree (no uncommitted changes).
- [ ] Run full test suite locally:
  ```bash
  PYTHONPATH=. pytest -q
  ```
- [ ] Verify CLI help works: `python -m opk.cli --help`.
- [ ] GUI smoke import (headless ok): `python -c "import opk.ui.main_window as _; print('GUI import OK')"`.

## 2) Version + changelog

- [ ] Bump `version` in `pyproject.toml`.
- [ ] Update `CHANGELOG.md` with highlights (features, fixes, docs) and date.

## 3) Docs

- [ ] Build docs locally with MkDocs:
  ```bash
  pip install .[docs]
  mkdocs build
  ```
- [ ] Update screenshots if UI changed:
  ```bash
  python -c "from opk.ui.screenshot import capture; import pathlib; capture(['main','rules','profiles','snippets','settings','preferences'], pathlib.Path('docs/images'))"
  ```
- [ ] Skim User Manual for out-of-date sections.

## 4) Packaging

- [ ] Build sdist/wheel:
  ```bash
  python -m pip install --upgrade build twine
  python -m build
  twine check dist/*
  ```
- [ ] Test install in a clean venv (with optional extras):
  ```bash
  python -m venv .venv-rel && source .venv-rel/bin/activate
  pip install dist/openprintkit-<VERSION>-py3-none-any.whl
  pip install "openprintkit[gui] @ file://$(pwd)/dist/openprintkit-<VERSION>-py3-none-any.whl"
  pip install "openprintkit[full] @ file://$(pwd)/dist/openprintkit-<VERSION>-py3-none-any.whl"
  ```

## 5) Tag + release

- [ ] Commit changes and tag:
  ```bash
  git add -A && git commit -m "release: v<VERSION>"
  git tag -a v<VERSION> -m "OpenPrintKit v<VERSION>"
  git push && git push --tags
  ```
- [ ] Create GitHub Release from the tag; attach highlights from the changelog.

## 6) Publish to PyPI

- [ ] Upload once satisfied:
  ```bash
  twine upload dist/*
  ```

## 7) Post-release

- [ ] Verify GitHub Pages docs site updated (workflow `docs.yml`).
- [ ] Update pinned installation snippets if the version appears in docs.
- [ ] Open an issue to track next milestones if needed.

Tip: Use optional extras:
- GUI: `pip install openprintkit[gui]`
- NFC: `pip install openprintkit[nfc]`
- Docs: `pip install openprintkit[docs]`
- Full: `pip install openprintkit[full]`
