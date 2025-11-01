from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _get_override_value(node: Any) -> Any:
    if isinstance(node, dict):
        # Cura defs sometimes use 'value' or 'default_value'
        if "value" in node:
            return node["value"]
        if "default_value" in node:
            return node["default_value"]
    return node


def _get_setting(data: Dict[str, Any], key: str) -> Any:
    if key in data:
        return data[key]
    ov = data.get("overrides") or data.get("settings") or {}
    if isinstance(ov, dict) and key in ov:
        return _get_override_value(ov[key])
    return None


def _norm_name(name: str) -> str:
    name = re.sub(r"\s+", "_", name.strip())
    name = re.sub(r"[^A-Za-z0-9_\-]", "", name)
    return name


def convert_cura_definition(path: Path) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    name = data.get("name") or (data.get("metadata") or {}).get("name") or path.stem
    width = _get_setting(data, "machine_width") or 0
    depth = _get_setting(data, "machine_depth") or 0
    height = _get_setting(data, "machine_height") or 0
    nozzle = _get_setting(data, "machine_nozzle_size") or 0.4
    heated = bool(_get_setting(data, "machine_heated_bed") or False)
    filament_diameter = _get_setting(data, "material_diameter") or 1.75

    pr: Dict[str, Any] = {
        "type": "printer",
        "name": name,
        "kinematics": "cartesian",
        "firmware": (data.get("metadata") or {}).get("firmware_name") or "Marlin",
        "nozzle_diameter": float(nozzle),
        "filament_diameter": float(filament_diameter),
        "build_volume": [float(width), float(depth), float(height)],
        "heated_bed": heated,
        "comments": "Generated from Cura definition via OPK converter (minimal mapping).",
    }
    return pr


def convert_cura_input(inp: Path, out_dir: Path) -> List[Path]:
    inp = Path(inp)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    files: Iterable[Path]
    if inp.is_dir():
        files = sorted(inp.glob("*.json"))
    else:
        files = [inp]
    for f in files:
        try:
            pr = convert_cura_definition(f)
        except Exception:
            # skip files that don't look like Cura definitions
            continue
        name = _norm_name(pr.get("name") or f.stem)
        outp = out_dir / f"{name}.json"
        outp.write_text(json.dumps(pr, indent=2), encoding="utf-8")
        written.append(outp)
    return written

