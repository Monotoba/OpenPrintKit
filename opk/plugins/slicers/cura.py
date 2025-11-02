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
    # Process defaults (optional)
    proc = (pdl.get('process_defaults') or {})
    lh = _num(proc.get('layer_height_mm') or 0.2)
    flh = _num(proc.get('first_layer_mm') or 0.28)
    spd = proc.get('speeds_mms') or {}
    speed_print = _num(spd.get('infill') or spd.get('perimeter') or 60)
    speed_travel = _num(spd.get('travel') or 150)
    # Retraction (optional)
    retract_len = _num(proc.get('retract_mm') or 0.0)
    retract_spd = _num(proc.get('retract_speed_mms') or 35.0)
    # Adhesion (optional)
    adhesion = proc.get('adhesion') or ''
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
        f'layer_height = {lh}',
        f'initial_layer_height = {flh}',
        f'line_width = {nozzle:.2f}',
        f'speed_print = {speed_print:.0f}',
        f'speed_travel = {speed_travel:.0f}',
        f'speed_infill = {speed_print:.0f}',
        f'speed_wall = {speed_print:.0f}',
        f'speed_wall_0 = {speed_print:.0f}',
        f'speed_wall_x = {speed_print:.0f}',
        f'retraction_enable = {1 if retract_len>0 else 0}',
        f'retraction_amount = {retract_len:.2f}',
        f'retraction_speed = {retract_spd:.0f}',
    ]
    if adhesion in ("skirt","brim","raft"):
        lines.append(f'adhesion_type = {adhesion}')
    cfg.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = cfg
    return out
