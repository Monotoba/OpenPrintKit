from __future__ import annotations
import json
import configparser
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _norm_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_","-") else "_" for c in (name or "")).strip("_") or "OPK_KISSlicer"


def convert_kisslicer_ini(path: Path) -> Dict[str, Any]:
    cp = configparser.ConfigParser(strict=False)
    # KISSlicer files may not have sections; fake a section header
    text = path.read_text(encoding='utf-8')
    if '[' not in text.splitlines()[0]:
        text = '[kiss]\n' + text
    cp.read_string(text)
    sec = cp[cp.sections()[0]] if cp.sections() else {}
    name = path.stem
    w = float(sec.get('machine_width', '200') or 200)
    d = float(sec.get('machine_depth', '200') or 200)
    z = float(sec.get('machine_height', '200') or 200)
    nozzle = float(sec.get('nozzle_diameter', '0.4') or 0.4)
    fdia = float(sec.get('filament_diameter', '1.75') or 1.75)
    pr: Dict[str, Any] = {
        'type': 'printer',
        'name': name,
        'kinematics': 'cartesian',
        'firmware': 'marlin',
        'nozzle_diameter': nozzle,
        'filament_diameter': fdia,
        'build_volume': [w, d, z],
        'comments': 'Generated from KISSlicer INI via OPK converter (best-effort).',
    }
    return pr


def convert_kisslicer_input(inp: Path, out_dir: Path) -> List[Path]:
    inp = Path(inp); out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files: Iterable[Path] = [inp] if inp.is_file() else sorted(inp.glob('*.ini'))
    written: List[Path] = []
    for f in files:
        try:
            pr = convert_kisslicer_ini(f)
        except Exception:
            continue
        name = _norm_name(pr.get('name') or f.stem)
        outp = out_dir / f"{name}.json"
        outp.write_text(json.dumps(pr, indent=2), encoding='utf-8')
        written.append(outp)
    return written

