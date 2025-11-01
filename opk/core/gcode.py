from __future__ import annotations
import re
from typing import Dict, Iterable, List, Set, Tuple

EXPLICIT_HOOK_KEYS: Tuple[str, ...] = (
    "start","end","on_abort","pause","resume","power_loss_resume","auto_shutdown",
    "tool_change","before_tool_change","after_tool_change","filament_change",
    "layer_change","before_layer_change","after_layer_change","top_layer_start","bottom_layer_start",
    "before_object","after_object","before_region","after_region",
    "retraction","unretraction","travel_start","travel_end","bridge_start","bridge_end",
    "support_interface_start","support_interface_end",
    "before_heating","after_heating","before_cooling",
    "on_progress_percent","on_layer_interval","on_time_interval",
    "before_snapshot","after_snapshot",
)


def list_hooks(gcode_obj: dict) -> List[str]:
    keys: Set[str] = set()
    for k in EXPLICIT_HOOK_KEYS:
        if isinstance(gcode_obj.get(k), list):
            keys.add(k)
    hooks = gcode_obj.get("hooks") or {}
    if isinstance(hooks, dict):
        keys.update(hooks.keys())
    return sorted(keys)


PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")


def find_placeholders(seq: Iterable[str]) -> Set[str]:
    found: Set[str] = set()
    for line in seq:
        for m in PLACEHOLDER_RE.finditer(line):
            found.add(m.group(1))
    return found


def _resolve_expr(expr: str, variables: Dict[str, object]):
    # Supports dotted paths and bracket indices: a.b[0].c
    cur = variables
    token_re = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)|(\[\d+\])")
    pos = 0
    while pos < len(expr):
        if expr[pos] == '.':
            pos += 1
            continue
        m = token_re.match(expr, pos)
        if not m:
            return None, False
        if m.group(1):  # identifier
            key = m.group(1)
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                return None, False
        else:  # index
            idx = int(expr[m.start(2)+1:m.end(2)-1])
            if isinstance(cur, (list, tuple)) and 0 <= idx < len(cur):
                cur = cur[idx]
            else:
                return None, False
        pos = m.end()
    return cur, True


def _render_line(line: str, variables: Dict[str, object]) -> Tuple[str, Set[str]]:
    missing: Set[str] = set()

    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        # Try direct
        if key in variables:
            return str(variables[key])
        # Try dotted/array expression
        val, ok = _resolve_expr(key, variables)
        if ok:
            return str(val)
        # Missing
        missing.add(key)
        return m.group(0)

    return PLACEHOLDER_RE.sub(repl, line), missing


def render_sequence(seq: Iterable[str], variables: Dict[str, object]) -> Tuple[List[str], Set[str]]:
    out: List[str] = []
    missing: Set[str] = set()
    for line in seq:
        r, miss = _render_line(line, variables)
        out.append(r)
        missing |= miss
    return out, missing


def apply_machine_control(pdl: Dict[str, object], base_gcode: Dict[str, List[str]] | None = None) -> Dict[str, List[str]]:
    """Translate pdl['machine_control'] into gcode.start/end additions.
    Returns a new gcode dict merging existing hooks with generated ones.
    """
    mc = (pdl or {}).get("machine_control") or {}
    g = {k: list(v) for k, v in ((base_gcode or {}).items())}
    start = list(g.get("start") or [])
    end = list(g.get("end") or [])

    def add(seq: List[str], cmd: str):
        if cmd and cmd not in seq:
            seq.append(cmd)

    if mc.get("psu_on_start"): add(start, "M80")
    if mc.get("psu_off_end"): add(end, "M81")
    if mc.get("light_on_start"): add(start, "M355 S1")
    if mc.get("light_off_end"): add(end, "M355 S0")

    rgb = mc.get("rgb_start") or {}
    r = int(rgb.get("r") or 0); gcol = int(rgb.get("g") or 0); b = int(rgb.get("b") or 0)
    if any(v > 0 for v in (r, gcol, b)):
        add(start, f"M150 R{r} U{gcol} B{b}")

    ch = mc.get("chamber") or {}
    temp = ch.get("temp")
    if isinstance(temp, (int, float)) and temp > 0:
        add(start, f"M141 S{int(temp)}")
        if ch.get("wait"):
            add(start, f"M191 S{int(temp)}")

    if mc.get("enable_mesh_start"): add(start, "M420 S1")
    if isinstance(mc.get("z_offset"), (int, float)) and mc.get("z_offset") != 0:
        add(start, f"M851 Z{float(mc['z_offset']):.2f}")

    for ln in mc.get("start_custom") or []:
        if isinstance(ln, str) and ln.strip(): add(start, ln)
    for ln in mc.get("end_custom") or []:
        if isinstance(ln, str) and ln.strip(): add(end, ln)

    # Peripherals
    cam = mc.get("camera") or {}
    cmd = (cam.get("command") or "M240").strip()
    if cam.get("use_before_snapshot") and cmd:
        bs = list(g.get("before_snapshot") or [])
        add(bs, cmd)
        g["before_snapshot"] = bs
    if cam.get("use_after_snapshot") and cmd:
        asq = list(g.get("after_snapshot") or [])
        add(asq, cmd)
        g["after_snapshot"] = asq

    sdl = mc.get("sd_logging") or {}
    if sdl.get("enable_start"):
        fn = sdl.get("filename") or "opk_log.gco"
        add(start, f"M928 {fn}")
        if sdl.get("stop_at_end"):
            add(end, "M29")

    fans = mc.get("fans") or {}
    def pct_to_s(p: float) -> int:
        try:
            return max(0, min(255, round(255.0 * float(p) / 100.0)))
        except Exception:
            return 0
    ps = fans.get("part_start_percent")
    if isinstance(ps, (int, float)) and ps > 0:
        add(start, f"M106 S{pct_to_s(ps)}")
    auxp = fans.get("aux_start_percent"); auxi = fans.get("aux_index")
    if isinstance(auxp, (int, float)) and auxp > 0 and isinstance(auxi, int):
        add(start, f"M106 P{auxi} S{pct_to_s(auxp)}")
    if fans.get("off_at_end"):
        add(end, "M107")
        if isinstance(auxi, int):
            add(end, f"M107 P{auxi}")

    # Exhaust control: prefer raw pin (M42) else fan index (M106/M107)
    ex = mc.get("exhaust") or {}
    if ex.get("enable_start"):
        sp = ex.get("speed_percent")
        s_val = pct_to_s(sp) if isinstance(sp, (int,float)) else 255
        pin = ex.get("pin"); fan = ex.get("fan_index")
        if (isinstance(pin, int) and pin >= 0) or isinstance(pin, str):
            pval = f'"{pin}"' if isinstance(pin, str) else str(pin)
            add(start, f"M42 P{pval} S{s_val}")
            if ex.get("off_at_end"):
                add(end, f"M42 P{pval} S0")
        elif isinstance(fan, int) and fan >= 0:
            add(start, f"M106 P{fan} S{s_val}")
            if ex.get("off_at_end"):
                add(end, f"M107 P{fan}")

    # Aux outputs (M42) — list of label/pin/start/end values
    for ao in (mc.get("aux_outputs") or []):
        pin = ao.get("pin")
        if not (isinstance(pin, int) or isinstance(pin, str)):
            continue
        pval = f'"{pin}"' if isinstance(pin, str) else str(pin)
        sv = ao.get("start_value"); ev = ao.get("end_value")
        if isinstance(sv, int): add(start, f"M42 P{pval} S{sv}")
        if isinstance(ev, int): add(end, f"M42 P{pval} S{ev}")

    # Custom peripherals: arbitrary hook → sequence
    for cp in (mc.get("custom_peripherals") or []):
        hook = cp.get("hook"); seq = cp.get("sequence")
        if not isinstance(hook, str) or not isinstance(seq, list):
            continue
        hook = hook.strip()
        cur = list(g.get(hook) or [])
        for ln in seq:
            if isinstance(ln, str) and ln.strip():
                add(cur, ln)
        g[hook] = cur

    out = dict(g)
    if start: out["start"] = start
    if end: out["end"] = end
    return out


def render_hooks_with_firmware(pdl: Dict[str, object]) -> Dict[str, List[str]]:
    """Return hooks merged from pdl['gcode'] and 'machine_control', applying
    simple firmware-specific policies where appropriate.
    """
    base = (pdl or {}).get("gcode") or {}
    out = apply_machine_control(pdl, base)
    firmware = str((pdl or {}).get("firmware") or "").lower()
    # Klipper: prefer host/macro messages for camera trigger (M240 alternative)
    if firmware == "klipper":
        def _map(seq: List[str] | None) -> List[str] | None:
            if not seq: return seq
            mapped: List[str] = []
            for s in seq:
                if isinstance(s, str) and s.strip().upper().startswith("M240"):
                    mapped.append("M118 TIMELAPSE_TAKE_FRAME")
                else:
                    mapped.append(s)
            return mapped
        out["before_snapshot"] = _map(out.get("before_snapshot")) or out.get("before_snapshot")
        out["after_snapshot"] = _map(out.get("after_snapshot")) or out.get("after_snapshot")
    # RepRapFirmware (RRF): map SD logging to M929 S1/S0
    if firmware in ("rrf", "reprap", "reprapfirmware", "duet"):
        def _replace_sd(seq: List[str] | None) -> List[str] | None:
            if not seq: return seq
            mapped: List[str] = []
            for s in seq:
                su = (s or "").strip().upper()
                if su.startswith("M928 "):
                    # M928 filename → M929 P"filename" S1
                    fn = s.split(maxsplit=1)[1] if len(s.split())>1 else "opk_log.gco"
                    mapped.append(f"M929 P\"{fn}\" S1")
                elif su == "M29":
                    mapped.append("M929 S0")
                else:
                    mapped.append(s)
            return mapped
        out["start"] = _replace_sd(out.get("start")) or out.get("start")
        out["end"] = _replace_sd(out.get("end")) or out.get("end")

    # GRBL/LinuxCNC: map exhaust to coolant (M7/M8 on, M9 off)
    if firmware in ("grbl", "linuxcnc"):
        mc = (pdl or {}).get("machine_control") or {}
        ex = mc.get("exhaust") or {}
        if ex.get("enable_start"):
            # choose flood coolant M8 for GRBL; mist M7 for LinuxCNC
            on = "M8" if firmware == "grbl" else "M7"
            seq = list(out.get("start") or [])
            add(seq, on)
            out["start"] = seq
        if ex.get("off_at_end"):
            seq = list(out.get("end") or [])
            add(seq, "M9")
            out["end"] = seq

    # OpenPrintTag injection: emit as comment block at start
    opt = (pdl or {}).get("open_print_tag") or {}
    if isinstance(opt, dict) and opt:
        import json as _json
        block = ";BEGIN:OPENPRINTTAG"
        payload = {k:v for k,v in opt.items() if v not in (None,"")}
        try:
            block_json = ";OPT:" + _json.dumps(payload, ensure_ascii=False)
        except Exception:
            block_json = ";OPT:{\"error\":\"invalid tag\"}"
        endb = ";END:OPENPRINTTAG"
        seq = list(out.get("start") or [])
        seq = [block, block_json, endb] + seq
        out["start"] = seq

    return out
