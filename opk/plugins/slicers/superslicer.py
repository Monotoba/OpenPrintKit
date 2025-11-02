from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from .prusa import _ensure_dir, _num, _bed_shape_str
from ...core.gcode import render_hooks_with_firmware


def generate_superslicer(pdl: Dict[str, Any], out_dir: Path) -> Dict[str, Path]:
    """Generate a SuperSlicer-style .ini file. SuperSlicer largely follows PrusaSlicer keys.

    This reuses most mappings from the Prusa generator with directory/label differences.
    """
    out: Dict[str, Path] = {}
    name = str(pdl.get('name') or 'OPK_SuperSlicer').replace(' ', '_')
    geom = pdl.get('geometry') or {}
    bed = geom.get('bed_shape') or [[0,0],[200,0],[200,200],[0,200]]
    ex0 = (pdl.get('extruders') or [{}])[0]
    nozzle = _num(ex0.get('nozzle_diameter') or 0.4)
    mat0 = (pdl.get('materials') or [{}])[0]
    mat_dia = _num(mat0.get('filament_diameter') or 1.75)
    noz_temp = _num(mat0.get('nozzle_temperature') or 205)
    bed_temp = _num(mat0.get('bed_temperature') or 60)
    # Process defaults
    proc = (pdl.get('process_defaults') or {})
    lh = _num(proc.get('layer_height_mm') or 0.2)
    flh = _num(proc.get('first_layer_mm') or 0.28)
    spd = proc.get('speeds_mms') or {}
    per_spd = _num(spd.get('perimeter') or 40)
    inf_spd = _num(spd.get('infill') or 60)
    trav_spd = _num(spd.get('travel') or 150)
    bed_str = _bed_shape_str(bed)
    hooks = render_hooks_with_firmware(pdl or {})
    start_g = '\n'.join(hooks.get('start') or [])
    end_g = '\n'.join(hooks.get('end') or [])
    sg = start_g.replace('\n','\\n')
    eg = end_g.replace('\n','\\n')
    ss_dir = out_dir / 'superslicer'
    _ensure_dir(ss_dir)
    ini_path = ss_dir / f'{name}.ini'
    lines = [
        f"[printer:{name}]",
        f"bed_shape = {bed_str}",
        f"nozzle_diameter = {nozzle:.2f}",
        f"min_layer_height = 0.07",
        f"max_layer_height = {nozzle:.2f}",
        f"start_gcode = {sg}",
        f"end_gcode = {eg}",
        "",
        f"[filament:{mat0.get('name') or 'Generic PLA'}]",
        f"filament_diameter = {mat_dia:.2f}",
        f"temperature = {noz_temp:.0f}",
        f"bed_temperature = {bed_temp:.0f}",
        "",
        f"[print:Standard]",
        f"layer_height = {lh}",
        f"first_layer_height = {flh}",
        f"perimeter_speed = {per_spd}",
        f"infill_speed = {inf_spd}",
        f"travel_speed = {trav_spd}",
    ]
    ini_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = ini_path
    return out

