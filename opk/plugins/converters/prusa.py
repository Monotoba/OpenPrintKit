from __future__ import annotations
import json
import configparser
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _norm_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_","-") else "_" for c in (name or "")).strip("_") or "OPK_Prusa"


def _parse_bed_shape(s: str) -> List[List[float]]:
    # format: 0x0,220x0,220x220,0x220
    pts: List[List[float]] = []
    try:
        for part in (s or "").split(','):
            x, y = part.split('x', 1)
            pts.append([float(x), float(y)])
    except Exception:
        pts = [[0,0],[200,0],[200,200],[0,200]]
    return pts


def _unescape_newlines(v: str) -> List[str]:
    v = v or ""
    return [ln for ln in v.replace('\\n', '\n').splitlines() if ln.strip()]


def convert_prusa_ini(path: Path) -> Dict[str, Any]:
    cp = configparser.ConfigParser()
    cp.read(path, encoding='utf-8')
    # pick first printer, filament, print sections
    prn_sec = next((s for s in cp.sections() if s.lower().startswith('printer:')), None)
    fil_sec = next((s for s in cp.sections() if s.lower().startswith('filament:')), None)
    prt_sec = next((s for s in cp.sections() if s.lower().startswith('print:')), None)
    prn = cp[prn_sec] if prn_sec else {}
    fil = cp[fil_sec] if fil_sec else {}
    name = (prn_sec.split(':',1)[1] if prn_sec and ':' in prn_sec else path.stem) or 'OPK_Prusa'
    bed_shape = _parse_bed_shape(prn.get('bed_shape', '0x0,200x0,200x200,0x200'))
    nozzle = float(prn.get('nozzle_diameter', 0.4)) if prn else 0.4
    fdia = float(fil.get('filament_diameter', 1.75)) if fil else 1.75
    # derive build volume from bed shape; Z unknown in INI, default 200
    xs = [p[0] for p in bed_shape]; ys = [p[1] for p in bed_shape]
    width = max(xs) - min(xs); depth = max(ys) - min(ys)
    start = _unescape_newlines(prn.get('start_gcode', ''))
    end = _unescape_newlines(prn.get('end_gcode', ''))
    pr: Dict[str, Any] = {
        "type": "printer",
        "name": name,
        "kinematics": "cartesian",
        "firmware": "marlin",
        "nozzle_diameter": nozzle,
        "filament_diameter": fdia,
        "build_volume": [float(width), float(depth), 200.0],
        "gcode": {"start": start, "end": end} if (start or end) else {},
        "comments": "Generated from Prusa-family INI via OPK converter (minimal mapping).",
    }
    return pr


def convert_prusa_input(inp: Path, out_dir: Path) -> List[Path]:
    inp = Path(inp); out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files: Iterable[Path] = [inp] if inp.is_file() else sorted(inp.glob('*.ini'))
    written: List[Path] = []
    for f in files:
        try:
            pr = convert_prusa_ini(f)
        except Exception:
            continue
        name = _norm_name(pr.get('name') or f.stem)
        outp = out_dir / f"{name}.json"
        outp.write_text(json.dumps(pr, indent=2), encoding='utf-8')
        written.append(outp)
    return written


def convert_superslicer_input(inp: Path, out_dir: Path) -> List[Path]:
    # Same INI structure as PrusaSlicer
    return convert_prusa_input(inp, out_dir)

