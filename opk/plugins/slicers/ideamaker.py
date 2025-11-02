from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from ...core.gcode import render_hooks_with_firmware


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _num(v, d=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(d)


def generate_ideamaker(pdl: Dict[str, Any], out_dir: Path) -> Dict[str, Path]:
    """Generate a minimal ideaMaker-style config (.cfg) with basic machine/material parameters.

    ideaMaker uses a binary profile format for full configs, but this text config is a reasonable starter.
    """
    out: Dict[str, Path] = {}
    name = str(pdl.get('name') or 'OPK_IdeaMaker').replace(' ', '_')
    geom = pdl.get('geometry') or {}
    bed = geom.get('bed_shape') or [[0,0],[200,0],[200,200],[0,200]]
    xs = [p[0] for p in bed]; ys = [p[1] for p in bed]
    w = max(xs) - min(xs); d = max(ys) - min(ys)
    z = _num(geom.get('z_height') or 200)
    ex0 = (pdl.get('extruders') or [{}])[0]
    nozzle = _num(ex0.get('nozzle_diameter') or 0.4)
    mat0 = (pdl.get('materials') or [{}])[0]
    mat_dia = _num(mat0.get('filament_diameter') or 1.75)
    noz_temp = _num(mat0.get('nozzle_temperature') or 205)
    bed_temp = _num(mat0.get('bed_temperature') or 60)
    hooks = render_hooks_with_firmware(pdl or {})
    start_g = '\n'.join(hooks.get('start') or [])
    end_g = '\n'.join(hooks.get('end') or [])
    # Process defaults
    proc = (pdl.get('process_defaults') or {})
    lh = _num(proc.get('layer_height_mm') or 0.2)
    flh = _num(proc.get('first_layer_mm') or 0.28)
    spd = proc.get('speeds_mms') or {}
    per_spd = _num(spd.get('perimeter') or 40)
    inf_spd = _num(spd.get('infill') or 60)
    trav_spd = _num(spd.get('travel') or 150)
    lines = [
        f'machineWidth = {int(w)}',
        f'machineDepth = {int(d)}',
        f'machineHeight = {int(z)}',
        f'nozzleDiameter = {nozzle:.2f}',
        f'filamentDiameter = {mat_dia:.2f}',
        f'printingTemperature = {noz_temp:.0f}',
        f'bedTemperature = {bed_temp:.0f}',
        f'layerHeight = {lh}',
        f'firstLayerHeight = {flh}',
        f'perimeterSpeed = {int(per_spd)}',
        f'infillSpeed = {int(inf_spd)}',
        f'travelSpeed = {int(trav_spd)}',
        f'startGcode = {start_g}',
        f'endGcode = {end_g}',
    ]
    outdir = out_dir / 'ideamaker'
    _ensure_dir(outdir)
    cfg = outdir / f'{name}.cfg'
    cfg.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = cfg
    return out
