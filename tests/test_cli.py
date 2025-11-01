import sys
from pathlib import Path
import pytest


def run_main(argv):
    from opk.cli.__main__ import main
    old = sys.argv[:]
    try:
        sys.argv = argv
        with pytest.raises(SystemExit) as e:
            main()
        return e.value.code
    finally:
        sys.argv = old


def test_cli_rules_examples(capsys):
    root = Path(__file__).resolve().parents[1] / "examples"
    code = run_main([
        "opk",
        "rules",
        "--printer", str(root / "printers/Longer_LK5_Pro_Marlin.json"),
        "--filament", str(root / "filaments/PLA_Baseline_LK5Pro.json"),
        "--process", str(root / "processes/Standard_0p20_LK5Pro.json"),
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "[SUMMARY]" in out


def test_cli_workspace_init(tmp_path: Path):
    code = run_main(["opk", "workspace", "init", str(tmp_path / "ws"), "--no-examples"])
    assert code == 0
    ws = tmp_path / "ws"
    # standard folders exist
    assert (ws / "profiles/printers").exists()
    assert (ws / "profiles/filaments").exists()
    assert (ws / "profiles/processes").exists()
    assert (ws / "bundles").exists()
    assert (ws / "logs").exists()
    # readme scaffold exists
    assert (ws / "README.opk-workspace.md").exists()

