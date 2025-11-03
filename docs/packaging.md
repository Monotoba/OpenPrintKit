# Packaging (CLI and GUI)

This guide covers installing OpenPrintKit from PyPI, building wheels/sdists, and shipping the GUI (OPK Studio).

## Install from PyPI

End users can install the CLI only or include optional extras:

```bash
# CLI only
pip install openprintkit

# CLI + GUI (OPK Studio)
pip install 'openprintkit[gui]'

# Full extras (GUI + NFC + docs tooling)
pip install 'openprintkit[full]'
```

Entry points installed:
- `opk` — CLI (`opk.cli.__main__:main`)
- `opk-gui` — GUI launcher (`opk.ui.main_window:main`)

Notes for GUI:
- On headless Linux or CI, set `QT_QPA_PLATFORM=offscreen` to avoid display errors.
- Wayland/X11 selection can be forced via `QT_QPA_PLATFORM=wayland` or `QT_QPA_PLATFORM=xcb`.

## Build packages locally

Use PEP 517 build with `build` and verify with `twine`:

```bash
python -m pip install --upgrade build twine
python -m build            # creates dist/*.tar.gz and dist/*.whl
twine check dist/*         # sanity checks metadata
```

Test installing the wheel in a clean environment:

```bash
python -m venv .venv-rel && source .venv-rel/bin/activate
pip install dist/openprintkit-<VERSION>-py3-none-any.whl
opk --help
```

Install with extras from the local wheel:

```bash
pip install "openprintkit[gui] @ file://$(pwd)/dist/openprintkit-<VERSION>-py3-none-any.whl"
```

## Release workflow (stub)

A GitHub Actions workflow `release.yml` is included to:
- build sdist/wheel on tag push `v*` or manual dispatch,
- optionally publish to PyPI via Trusted Publishing.

To enable publishing:
1) Configure the project on PyPI for Trusted Publishing, linking this GitHub repository.
2) Create a GitHub Release tagged `vX.Y.Z`.
3) The `publish-pypi` job will upload artifacts from `dist/`.

If you prefer TestPyPI, update the workflow step to set `repository-url` and API token.

## Windows/macOS notes (GUI)

PySide6 provides prebuilt wheels for major Python versions. If wheels are unavailable for bleeding‑edge Python versions/OS, GUI import may fall back to stubs or fail to launch until wheels land.

For distribution as a single binary, consider PyInstaller or Briefcase (not configured here). Start with PyInstaller:

```bash
pip install pyinstaller
pyinstaller -F -n opk-gui -w -i NONE -s -y -p . -m opk.ui.main_window
```

Adjust hidden imports per GUI modules as needed.

