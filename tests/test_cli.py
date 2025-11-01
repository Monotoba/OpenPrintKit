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


def test_cli_install_dry_run(tmp_path: Path, capsys):
    # Prepare source and dest with one add, one update, one same
    src = tmp_path / "src"; dest = tmp_path / "dest"
    src.mkdir(parents=True, exist_ok=True); dest.mkdir(parents=True, exist_ok=True)
    (src / "printers").mkdir(parents=True, exist_ok=True)
    (src / "filaments").mkdir(parents=True, exist_ok=True)
    (src / "processes").mkdir(parents=True, exist_ok=True)
    (dest / "printers").mkdir(parents=True, exist_ok=True)
    (dest / "filaments").mkdir(parents=True, exist_ok=True)

    import json
    (src / "printers/a.json").write_text(json.dumps({"type":"printer","name":"A","nozzle_diameter":0.4,"filament_diameter":1.75,"build_volume":[100,100,100]}), encoding="utf-8")
    (src / "filaments/f.json").write_text(json.dumps({"type":"filament","name":"F","filament_type":"PLA","nozzle_temperature":200,"bed_temperature":60}), encoding="utf-8")
    (src / "processes/p.json").write_text(json.dumps({"type":"process","name":"P","layer_height":0.2,"print_speed":60}), encoding="utf-8")
    # same printer
    (dest / "printers/a.json").write_text(json.dumps({"type":"printer","name":"A","nozzle_diameter":0.4,"filament_diameter":1.75,"build_volume":[100,100,100]}), encoding="utf-8")
    # update filament
    (dest / "filaments/f.json").write_text(json.dumps({"type":"filament","name":"F","filament_type":"PLA","nozzle_temperature":205,"bed_temperature":60}), encoding="utf-8")

    code = run_main(["opk", "install", "--src", str(src), "--dest", str(dest), "--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert "[ADD" in out and "[UPDATE" in out and "[SAME" in out
    assert "[SUMMARY]" in out


def test_cli_pdl_validate(tmp_path: Path, capsys):
    pdl = tmp_path / "test.yaml"
    pdl.write_text("""\
pdl_version: "1.0"
id: test
name: Test
firmware: marlin
kinematics: cartesian
geometry:
  bed_shape: [[0,0],[200,0],[200,200],[0,200]]
  z_height: 200
extruders: [{ nozzle_diameter: 0.4 }]
machine_control:
  camera: { use_before_snapshot: true, command: "M240" }
""", encoding="utf-8")
    code = run_main(["opk", "pdl-validate", "--pdl", str(pdl)])
    assert code == 0
    out = capsys.readouterr().out
    assert "[SUMMARY]" in out
