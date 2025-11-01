from pathlib import Path
from opk.core.install import plan_install, perform_install
import json


def write_json(p: Path, obj: dict):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, sort_keys=True, indent=2), encoding="utf-8")


def test_plan_install(tmp_path: Path):
    src = tmp_path / "src"; dest = tmp_path / "dest"
    write_json(src / "printers/a.json", {"type": "printer", "name": "A", "nozzle_diameter": 0.4, "filament_diameter": 1.75, "build_volume": [100,100,100]})
    write_json(src / "filaments/f.json", {"type": "filament", "name": "F", "filament_type": "PLA", "nozzle_temperature": 200, "bed_temperature": 60})
    write_json(src / "processes/p.json", {"type": "process", "name": "P", "layer_height": 0.2, "print_speed": 60})
    # dest has same printer and different filament
    write_json(dest / "printers/a.json", {"type": "printer", "name": "A", "nozzle_diameter": 0.4, "filament_diameter": 1.75, "build_volume": [100,100,100]})
    write_json(dest / "filaments/f.json", {"type": "filament", "name": "F", "filament_type": "PLA", "nozzle_temperature": 205, "bed_temperature": 60})

    ops = plan_install(src, dest)
    statuses = {(op.category, op.name): op.status for op in ops}
    assert statuses[("printers", "a.json")] == "same"
    assert statuses[("filaments", "f.json")] == "update"
    assert statuses[("processes", "p.json")] == "add"


def test_perform_install_with_backup(tmp_path: Path):
    src = tmp_path / "src"; dest = tmp_path / "dest"; backup = tmp_path / "backup.zip"
    write_json(src / "printers/a.json", {"type": "printer", "name": "A", "nozzle_diameter": 0.4, "filament_diameter": 1.75, "build_volume": [100,100,100]})
    write_json(dest / "printers/a.json", {"type": "printer", "name": "A", "nozzle_diameter": 0.5, "filament_diameter": 1.75, "build_volume": [100,100,100]})
    ops = plan_install(src, dest)
    res = perform_install(ops, backup_zip=backup)
    assert res["written"] == 1
    assert backup.exists()
    # dest file updated to match src
    import json as _json
    data = _json.loads((dest / "printers/a.json").read_text(encoding="utf-8"))
    assert data["nozzle_diameter"] == 0.4
