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


def generate_bambu(pdl: Dict[str, Any], out_dir: Path) -> Dict[str, Path]:
    """Generate a minimal Bambu Studio-style .ini (Prusa-like) with basic keys.

    Bambu Studio accepts Prusa-style configs for many parameters; this is a starter config.
    """
    out: Dict[str, Path] = {}
    name = str(pdl.get('name') or 'OPK_Bambu').replace(' ', '_')
    geom = pdl.get('geometry') or {}
    bed = geom.get('bed_shape') or [[0,0],[256,0],[256,256],[0,256]]
    xs = [p[0] for p in bed]; ys = [p[1] for p in bed]
    w = max(xs) - min(xs); d = max(ys) - min(ys)
    z = _num(geom.get('z_height') or 256)
    ex0 = (pdl.get('extruders') or [{}])[0]
    nozzle = _num(ex0.get('nozzle_diameter') or 0.4)
    mat0 = (pdl.get('materials') or [{}])[0]
    mat_dia = _num(mat0.get('filament_diameter') or 1.75)
    noz_temp = _num(mat0.get('nozzle_temperature') or 205)
    bed_temp = _num(mat0.get('bed_temperature') or 60)
    hooks = render_hooks_with_firmware(pdl or {})
    start_g = '\n'.join(hooks.get('start') or [])
    end_g = '\n'.join(hooks.get('end') or [])
    bdir = out_dir / 'bambu'
    _ensure_dir(bdir)
    ini = bdir / f'{name}.ini'
    sg = start_g.replace('\n','\\n')
    eg = end_g.replace('\n','\\n')
    lines = [
        f"[printer:{name}]",
        f"bed_shape = 0x0,{int(w)}x0,{int(w)}x{int(d)},0x{int(d)}",
        f"nozzle_diameter = {nozzle:.2f}",
        f"start_gcode = {sg}",
        f"end_gcode = {eg}",
        "",
        f"[filament:{mat0.get('name') or 'Generic PLA'}]",
        f"filament_diameter = {mat_dia:.2f}",
        f"temperature = {noz_temp:.0f}",
        f"bed_temperature = {bed_temp:.0f}",
    ]
    ini.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    out['profile'] = ini
    return out
