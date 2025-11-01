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


def generate_cura(pdl: Dict[str, Any], out_dir: Path) -> Dict[str, Path]:
    """Generate a minimal Cura-compatible .cfg profile from PDL fields.

    Note: Cura has multiple profile layers (machine/material/quality). This function emits
    a single combined profile.cfg with key parameters derived from PDL as a convenient starting point.
    """
    out: Dict[str, Path] = {}
    name = str(pdl.get('name') or 'OPK_Printer').replace(' ', '_')
    geom = pdl.get('geometry') or {}
    bed = geom.get('bed_shape') or [[0,0],[200,0],[200,200],[0,200]]
    z = _num(geom.get('z_height') or 200)
    xs = [p[0] for p in bed]; ys = [p[1] for p in bed]
    w = max(xs) - min(xs); d = max(ys) - min(ys)
    ex0 = (pdl.get('extruders') or [{}])[0]
    nozzle = _num(ex0.get('nozzle_diameter') or 0.4)
    mat0 = (pdl.get('materials') or [{}])[0]
    mat_dia = _num(mat0.get('filament_diameter') or 1.75)
    noz_temp = _num(mat0.get('nozzle_temperature') or 205)
    bed_temp = _num(mat0.get('bed_temperature') or 60)
    process_speed = 60.0
    # path
    cdir = out_dir / 'cura'
    _ensure_dir(cdir)
    cfg = cdir / f'{name}_profile.cfg'
    lines = [
        f'machine_width = {w:.0f}',
        f'machine_depth = {d:.0f}',
        f'machine_height = {z:.0f}',
        f'machine_nozzle_size = {nozzle:.2f}',
        f'material_diameter = {mat_dia:.2f}',
        f'material_print_temperature = {noz_temp:.0f}',
        f'material_bed_temperature = {bed_temp:.0f}',
        f'layer_height = {0.2}',
        f'line_width = {nozzle:.2f}',
        f'speed_print = {process_speed:.0f}',
    ]
    cfg.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = cfg
    return out

