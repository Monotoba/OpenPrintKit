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
    ext_per_spd = _num(spd.get('external_perimeter') or 0)
    top_spd = _num(spd.get('top') or spd.get('top_solid') or 0)
    bot_spd = _num(spd.get('bottom') or spd.get('bottom_solid') or 0)
    # Extrusion multiplier (filament flow)
    ext_mult = proc.get('extrusion_multiplier')
    # Retraction (filament-level)
    retr_len = _num(proc.get('retract_mm') or 0.0)
    retr_spd = _num(proc.get('retract_speed_mms') or 0.0)
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
        *( [f"extrusion_multiplier = {float(ext_mult):.2f}"] if isinstance(ext_mult, (int,float)) else [] ),
        *( [f"retract_length = {retr_len:.2f}"] if retr_len > 0 else [] ),
        *( [f"retract_speed = {int(retr_spd)}"] if retr_spd > 0 else [] ),
        "",
        f"[print:Standard]",
        f"layer_height = {lh}",
        f"first_layer_height = {flh}",
        f"perimeter_speed = {per_spd}",
        f"infill_speed = {inf_spd}",
        f"travel_speed = {trav_spd}",
    ]
    if ext_per_spd:
        lines.append(f'external_perimeter_speed = {ext_per_spd}')
    if top_spd:
        lines.append(f'top_solid_infill_speed = {top_spd}')
    if bot_spd:
        lines.append(f'bottom_solid_infill_speed = {bot_spd}')
    # Infill density (percent)
    try:
        infill_pct = int(float((proc.get('infill_percent') if isinstance(proc, dict) else 0) or 0))
        if infill_pct:
            lines.append(f'fill_density = {infill_pct}')
    except Exception:
        pass
    # Supports (best-effort)
    support = (proc.get('support') if isinstance(proc, dict) else None)
    if isinstance(support, bool):
        lines.append(f'support_material = {1 if support else 0}')
    elif isinstance(support, str) and support:
        lines.append('support_material = 1')
        lines.append(f'support_material_pattern = {support}')
    # Optional per-section accelerations
    acc = (proc.get('accelerations_mms2') or {})
    per_acc = _num(acc.get('perimeter') or 0)
    inf_acc = _num(acc.get('infill') or 0)
    trav_acc = _num(acc.get('travel') or 0)
    if per_acc:
        lines.append(f'perimeter_acceleration = {int(per_acc)}')
    if inf_acc:
        lines.append(f'infill_acceleration = {int(inf_acc)}')
    if trav_acc:
        lines.append(f'travel_acceleration = {int(trav_acc)}')
    # Global accel limits
    lim = (pdl.get('limits') or {})
    try:
        amax = int(float(lim.get('acceleration_max') or 0))
    except Exception:
        amax = 0
    if amax:
        lines.append(f'max_print_acceleration = {amax}')
        lines.append(f'max_travel_acceleration = {amax}')
    # Adhesion and cooling
    adhesion = (proc.get('adhesion') or '').lower()
    if adhesion == 'brim':
        lines.append('brim_width = 5')
    elif adhesion == 'skirt':
        lines.append('skirts = 1')
    # Walls and infill pattern
    walls = proc.get('walls') if isinstance(proc, dict) else None
    try:
        if walls is not None:
            lines.append(f'perimeters = {int(walls)}')
    except Exception:
        pass
    inf_pat = (proc.get('infill_pattern') if isinstance(proc, dict) else None)
    if isinstance(inf_pat, str) and inf_pat:
        lines.append(f'fill_pattern = {inf_pat}')
    cooling = proc.get('cooling') or {}
    mlt = int(cooling.get('min_layer_time_s') or 0)
    fmin = int(cooling.get('fan_min_percent') or 0)
    fmax = int(cooling.get('fan_max_percent') or 0)
    always = bool(cooling.get('fan_always_on') or False)
    if mlt:
        lines.append(f'min_layer_time = {mlt}')
    if fmin or fmax or always:
        lines.append(f'fan_always_on = {1 if always else 0}')
    if fmin:
        lines.append(f'min_fan_speed = {fmin}')
    if fmax:
        lines.append(f'max_fan_speed = {fmax}')
    ini_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = ini_path
    return out
