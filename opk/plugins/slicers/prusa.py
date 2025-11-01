from __future__ import annotations
from pathlib import Path
from typing import Dict, Any


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _num(v, d=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(d)


def _bed_shape_str(bed) -> str:
    try:
        xs = [p[0] for p in bed]; ys = [p[1] for p in bed]
        w = max(xs) - min(xs); d = max(ys) - min(ys)
    except Exception:
        w, d = 200, 200
    return f"0x0,{int(w)}x0,{int(w)}x{int(d)},0x{int(d)}"


def generate_prusa(pdl: Dict[str, Any], out_dir: Path) -> Dict[str, Path]:
    """Generate a minimal PrusaSlicer-style .ini file with printer/filament/print settings.

    This is a starter config; users can import into PrusaSlicer and refine.
    """
    out: Dict[str, Path] = {}
    name = str(pdl.get('name') or 'OPK_Prusa').replace(' ', '_')
    geom = pdl.get('geometry') or {}
    bed = geom.get('bed_shape') or [[0,0],[200,0],[200,200],[0,200]]
    lh = 0.2
    ex0 = (pdl.get('extruders') or [{}])[0]
    nozzle = _num(ex0.get('nozzle_diameter') or 0.4)
    mat0 = (pdl.get('materials') or [{}])[0]
    mat_dia = _num(mat0.get('filament_diameter') or 1.75)
    noz_temp = _num(mat0.get('nozzle_temperature') or 205)
    bed_temp = _num(mat0.get('bed_temperature') or 60)
    prusa_dir = out_dir / 'prusa'
    _ensure_dir(prusa_dir)
    ini_path = prusa_dir / f'{name}.ini'
    bed_str = _bed_shape_str(bed)
    lines = [
        f"[printer:{name}]",
        f"bed_shape = {bed_str}",
        f"nozzle_diameter = {nozzle:.2f}",
        f"min_layer_height = 0.07",
        f"max_layer_height = {nozzle:.2f}",
        "",
        f"[filament:{mat0.get('name') or 'Generic PLA'}]",
        f"filament_diameter = {mat_dia:.2f}",
        f"temperature = {noz_temp:.0f}",
        f"bed_temperature = {bed_temp:.0f}",
        "",
        f"[print:Standard]",
        f"layer_height = {lh}",
        f"first_layer_height = 0.28",
    ]
    ini_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = ini_path
    return out

