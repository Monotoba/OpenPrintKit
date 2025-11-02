from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _norm_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_","-") else "_" for c in (name or "")).strip("_") or "OPK_IdeaMaker"


def _parse_cfg(path: Path) -> Dict[str, str]:
    kv: Dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            kv[k.strip()] = v.strip()
    return kv


def convert_ideamaker_cfg(path: Path) -> Dict[str, Any]:
    kv = _parse_cfg(path)
    name = path.stem
    w = float(kv.get('machineWidth', '200') or 200)
    d = float(kv.get('machineDepth', '200') or 200)
    z = float(kv.get('machineHeight', '200') or 200)
    nozzle = float(kv.get('nozzleDiameter', '0.4') or 0.4)
    fdia = float(kv.get('filamentDiameter', '1.75') or 1.75)
    pr: Dict[str, Any] = {
        'type': 'printer',
        'name': name,
        'kinematics': 'cartesian',
        'firmware': 'marlin',
        'nozzle_diameter': nozzle,
        'filament_diameter': fdia,
        'build_volume': [w, d, z],
        'comments': 'Generated from ideaMaker CFG via OPK converter (minimal mapping).',
    }
    return pr


def convert_ideamaker_input(inp: Path, out_dir: Path) -> List[Path]:
    inp = Path(inp); out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files: Iterable[Path] = [inp] if inp.is_file() else sorted(inp.glob('*.cfg'))
    written: List[Path] = []
    for f in files:
        try:
            pr = convert_ideamaker_cfg(f)
        except Exception:
            continue
        name = _norm_name(pr.get('name') or f.stem)
        outp = out_dir / f"{name}.json"
        outp.write_text(json.dumps(pr, indent=2), encoding='utf-8')
        written.append(outp)
    return written

