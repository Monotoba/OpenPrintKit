from __future__ import annotations
from typing import Dict, List, Any

class Issue:
    def __init__(self, level: str, message: str, path: str = ""):
        self.level = level  # 'error' | 'warn' | 'info'
        self.message = message
        self.path = path
    def as_dict(self): return {"level": self.level, "message": self.message, "path": self.path}

def _num(x) -> float | None:
    try: return float(x)
    except Exception: return None

def validate_printer(pr: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []
    nd = _num(pr.get("nozzle_diameter"))
    fd = _num(pr.get("filament_diameter"))
    if nd is not None and not (0.1 <= nd <= 1.2):
        issues.append(Issue("warn", "Unusual nozzle_diameter (0.1–1.2 mm typical)", "nozzle_diameter"))
    if fd is not None and not (1.6 <= fd <= 3.1):
        issues.append(Issue("warn", "Unusual filament_diameter (1.75 or 2.85 typical)", "filament_diameter"))
    bv = pr.get("build_volume")
    if isinstance(bv, list) and len(bv) == 3:
        if any((_num(v) or 0) <= 0 for v in bv):
            issues.append(Issue("error", "build_volume must be positive [X,Y,Z]", "build_volume"))
    return issues

def validate_process(proc: Dict[str, Any], printer: Dict[str, Any] | None = None) -> List[Issue]:
    issues: List[Issue] = []
    nozzle = _num((printer or {}).get("nozzle_diameter"))
    lh = _num(proc.get("layer_height"))
    flh = _num(proc.get("first_layer_height"))
    ps = _num(proc.get("print_speed"))
    ts = _num(proc.get("travel_speed"))
    adhesion = (proc.get("adhesion_type") or "").lower()

    if nozzle and lh and lh > 0.8 * nozzle:
        issues.append(Issue("warn", f"layer_height {lh} > 80% of nozzle {nozzle}", "layer_height"))
    if nozzle and flh and flh > 0.8 * nozzle:
        issues.append(Issue("warn", f"first_layer_height {flh} > 80% of nozzle {nozzle}", "first_layer_height"))
    if ps and ps > 150:
        issues.append(Issue("warn", "print_speed unusually high (>150 mm/s)", "print_speed"))
    if ts and ts > 300:
        issues.append(Issue("warn", "travel_speed unusually high (>300 mm/s)", "travel_speed"))
    if adhesion not in {"skirt", "brim", "raft", "none", ""}:
        issues.append(Issue("warn", f"Unknown adhesion_type '{adhesion}'", "adhesion_type"))
    return issues

def validate_filament(fil: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []
    mat = (fil.get("filament_type") or "").upper()
    nt = _num(fil.get("nozzle_temperature"))
    bt = _num(fil.get("bed_temperature"))
    if mat == "PLA":
        if nt is not None and not (180 <= nt <= 230):
            issues.append(Issue("warn", "PLA nozzle temp usually 180–230 °C", "nozzle_temperature"))
        if bt is not None and not (0 <= bt <= 70):
            issues.append(Issue("warn", "PLA bed temp usually 0–70 °C", "bed_temperature"))
    return issues

def summarize(*issue_lists: List[Issue]) -> Dict[str, int]:
    flat = [i for lst in issue_lists for i in lst]
    return {
        "error": sum(1 for i in flat if i.level == "error"),
        "warn": sum(1 for i in flat if i.level == "warn"),
        "info": sum(1 for i in flat if i.level == "info"),
        "total": len(flat),
    }


def validate_pdl(pdl: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []
    mc = (pdl or {}).get("machine_control") or {}
    fw = str((pdl or {}).get("firmware") or "").lower()
    fans = mc.get("fans") or {}
    rgb = (mc.get("rgb_start") or {}) if isinstance(mc.get("rgb_start"), dict) else {}
    materials = (pdl or {}).get("materials") or []
    extruders = (pdl or {}).get("extruders") or []
    # Exhaust: warn if both pin and fan_index set (ambiguous)
    ex = mc.get("exhaust") or {}
    if ex.get("pin") is not None and ex.get("fan_index") is not None:
        issues.append(Issue("warn", "Exhaust has both pin and fan_index set; pin will take precedence", "machine_control.exhaust"))
    # Camera: warn if triggers set but command empty
    cam = mc.get("camera") or {}
    if (cam.get("use_before_snapshot") or cam.get("use_after_snapshot")) and not (cam.get("command") or "").strip():
        issues.append(Issue("warn", "Camera trigger enabled but command is empty", "machine_control.camera.command"))
    # Aux outputs: check duplicate pins
    pins = []
    for idx, ao in enumerate(mc.get("aux_outputs") or []):
        try:
            p = int(ao.get("pin"))
            if p in pins:
                issues.append(Issue("warn", f"Duplicate aux pin P{p}", f"machine_control.aux_outputs[{idx}].pin"))
            pins.append(p)
        except Exception:
            issues.append(Issue("warn", "Aux output pin is not an integer", f"machine_control.aux_outputs[{idx}].pin"))
    # Custom peripherals: ensure hook and sequence shape
    for idx, cp in enumerate(mc.get("custom_peripherals") or []):
        if not isinstance(cp.get("hook"), str) or not cp.get("hook"):
            issues.append(Issue("warn", "Custom peripheral hook should be a non-empty string", f"machine_control.custom_peripherals[{idx}].hook"))
        if not isinstance(cp.get("sequence"), list) or not cp.get("sequence"):
            issues.append(Issue("warn", "Custom peripheral sequence should be a non-empty list", f"machine_control.custom_peripherals[{idx}].sequence"))
    # Firmware-specific guidance
    if fw in ("grbl", "linuxcnc"):
        if (ex.get("enable_start")) and not ex.get("off_at_end"):
            issues.append(Issue("warn", "GRBL/LinuxCNC exhaust maps to coolant (M8 on/M9 off); set off_at_end to ensure M9 is emitted", "machine_control.exhaust.off_at_end"))
        if ex.get("pin") is not None and ex.get("pin") != "":
            issues.append(Issue("info", "GRBL/LinuxCNC ignores raw pin control for exhaust; using M7/M8/M9 coolant mapping instead", "machine_control.exhaust.pin"))
        # Fans are not standard in GRBL/LinuxCNC; advise coolant or custom peripherals
        if (fans.get("part_start_percent") or 0) > 0 or (fans.get("aux_start_percent") or 0) > 0 or isinstance(fans.get("aux_index"), int):
            issues.append(Issue("info", "GRBL/LinuxCNC: fan commands (M106/M107) are not standard; prefer coolant (M7/M8/M9) or custom peripherals", "machine_control.fans"))
        # SD logging/camera often not applicable
        sdl = mc.get("sd_logging") or {}
        if sdl.get("enable_start"):
            issues.append(Issue("info", "GRBL/LinuxCNC: SD logging G-codes may not be supported; consider host-side logging", "machine_control.sd_logging"))
        if cam.get("use_before_snapshot") or cam.get("use_after_snapshot"):
            issues.append(Issue("info", "GRBL/LinuxCNC: camera triggers require custom macros or HAL integration", "machine_control.camera"))
    if fw == "klipper":
        cam_cmd = (cam.get("command") or "").strip().upper()
        if (cam.get("use_before_snapshot") or cam.get("use_after_snapshot")) and cam_cmd.startswith("M240"):
            issues.append(Issue("info", "Klipper: camera M240 will be mapped to 'M118 TIMELAPSE_TAKE_FRAME' by policy", "machine_control.camera.command"))
        # Klipper typically maps M106/M107 to macros; hint if fans used
        if (fans.get("part_start_percent") or 0) > 0 or (fans.get("aux_start_percent") or 0) > 0:
            issues.append(Issue("info", "Klipper: M106/M107 are often implemented as macros; ensure your printer.cfg defines fan aliases", "machine_control.fans"))
        sdl = mc.get("sd_logging") or {}
        if sdl.get("enable_start"):
            issues.append(Issue("info", "Klipper: SD logging is typically host-driven; ensure macros exist if you rely on G-codes", "machine_control.sd_logging"))
    # RRF / RepRapFirmware guidance
    if fw in ("rrf", "reprap", "reprapfirmware", "duet"):
        sdl = mc.get("sd_logging") or {}
        if sdl.get("enable_start"):
            issues.append(Issue("info", "RRF: SD logging uses M929 P\"filename\" S1 / M929 S0 (mapped from M928/M29)", "machine_control.sd_logging"))
            fn = sdl.get("filename")
            if isinstance(fn, str) and " " in fn:
                issues.append(Issue("warn", "RRF: SD log filename contains spaces; ensure your firmware accepts this name", "machine_control.sd_logging.filename"))
        if isinstance(ex.get("pin"), int):
            issues.append(Issue("info", "RRF: prefer named pins (e.g., out1) instead of numeric pins for exhaust", "machine_control.exhaust.pin"))
        fans = mc.get("fans") or {}
        if isinstance(fans.get("aux_index"), int) and (fans.get("aux_start_percent") not in (None, 0)) and not fans.get("off_at_end"):
            issues.append(Issue("warn", "Aux fan configured without off_at_end; add off_at_end to emit M107 P at end", "machine_control.fans.off_at_end"))
        # RGB tips
        if any((rgb.get("r",0), rgb.get("g",0), rgb.get("b",0))):
            issues.append(Issue("info", "RRF: RGB is set via M150; mapping will emit M150 Rnn Unn Bnn", "machine_control.rgb_start"))
        # Aux fan index guidance
        if (fans.get("aux_start_percent") not in (None, 0)) and not isinstance(fans.get("aux_index"), int):
            issues.append(Issue("warn", "RRF: aux_start_percent set without aux_index; specify fan P index (e.g., P1)", "machine_control.fans.aux_index"))
        # Aux outputs prefer named pins
        for i, ao in enumerate(mc.get("aux_outputs") or []):
            if isinstance(ao, dict) and isinstance(ao.get("pin"), int):
                issues.append(Issue("info", "RRF: prefer named pins (e.g., out1) for aux_outputs", f"machine_control.aux_outputs[{i}].pin"))
    # Marlin guidance
    if fw == "marlin":
        if isinstance(ex.get("pin"), str) and (ex.get("pin") or "").strip():
            issues.append(Issue("warn", "Marlin M42 expects numeric pin values; string pins unsupported — use fan_index (M106/M107) or numeric P", "machine_control.exhaust.pin"))
        sdl = mc.get("sd_logging") or {}
        if sdl.get("enable_start"):
            issues.append(Issue("info", "Marlin: SD logging uses M928 filename (start) / M29 (stop)", "machine_control.sd_logging"))
            fn = sdl.get("filename")
            if isinstance(fn, str) and " " in fn:
                issues.append(Issue("warn", "Marlin: SD log filename contains spaces; consider using underscores", "machine_control.sd_logging.filename"))
        # RGB via M150 often needs NeoPixel setup
        if any((rgb.get("r",0), rgb.get("g",0), rgb.get("b",0))):
            issues.append(Issue("info", "Marlin: RGB commonly uses M150; ensure NEOPIXEL or LED support is enabled", "machine_control.rgb_start"))
        # Fans: remind to turn off
        if ((fans.get("part_start_percent") or 0) > 0 or (fans.get("aux_start_percent") or 0) > 0) and not fans.get("off_at_end"):
            issues.append(Issue("info", "Marlin: consider 'Fans off at end' to emit M107", "machine_control.fans.off_at_end"))
        # Mesh enable → suggest Z offset
        if bool(mc.get("enable_mesh_start")) and (_num(mc.get("z_offset")) in (None, 0)):
            issues.append(Issue("info", "Marlin: mesh enabled; consider setting probe Z offset (M851)", "machine_control.z_offset"))
    # Smoothieware guidance (best-effort)
    if fw in ("smoothie", "smoothieware"):
        if (fans.get("part_start_percent") or 0) > 0 or (fans.get("aux_start_percent") or 0) > 0:
            issues.append(Issue("info", "Smoothieware: use M106/M107; ensure fan modules are configured in config.txt", "machine_control.fans"))
        if any((rgb.get("r",0), rgb.get("g",0), rgb.get("b",0))):
            issues.append(Issue("info", "Smoothieware: RGB via M150 may require LED module support", "machine_control.rgb_start"))
    # Repetier guidance (best-effort)
    if fw == "repetier":
        if (fans.get("part_start_percent") or 0) > 0:
            issues.append(Issue("info", "Repetier: fans controlled with M106/M107; verify P index mapping", "machine_control.fans"))
        if any((rgb.get("r",0), rgb.get("g",0), rgb.get("b",0))):
            issues.append(Issue("info", "Repetier: M150 availability depends on build; otherwise use custom commands", "machine_control.rgb_start"))
    # Bambu guidance (info-only)
    if fw == "bambu":
        if (mc.get("psu_on_start") or mc.get("psu_off_end") or (fans.get("part_start_percent") or 0) > 0):
            issues.append(Issue("info", "Bambu: G-code support is limited; prefer minimal start/end and printer-side macros when possible", "machine_control"))
        if (cam.get("use_before_snapshot") or cam.get("use_after_snapshot")) or (mc.get("sd_logging") or {}).get("enable_start"):
            issues.append(Issue("info", "Bambu: camera and SD logging should be managed by built-in features when available", "machine_control"))

    # PDL-level process defaults checks (if present)
    pd = (pdl or {}).get("process_defaults") or {}
    # Layer heights vs nozzle (use first extruder if present)
    try:
        ex0 = ((pdl or {}).get("extruders") or [{}])[0]
    except Exception:
        ex0 = {}
    nz = _num(ex0.get("nozzle_diameter"))
    lh = _num(pd.get("layer_height_mm"))
    flh = _num(pd.get("first_layer_mm"))
    if nz and lh and lh > 0.8 * nz:
        issues.append(Issue("warn", f"layer_height_mm {lh} > 80% of nozzle {nz}", "process_defaults.layer_height_mm"))
    if nz and flh and flh > 0.8 * nz:
        issues.append(Issue("warn", f"first_layer_mm {flh} > 80% of nozzle {nz}", "process_defaults.first_layer_mm"))
    # Cooling sanity
    cool = pd.get("cooling") or {}
    for k in ("fan_min_percent", "fan_max_percent"):
        v = _num(cool.get(k))
        if v is not None and not (0 <= v <= 100):
            issues.append(Issue("warn", f"{k} must be between 0 and 100", f"process_defaults.cooling.{k}"))
    mlt = _num(cool.get("min_layer_time_s"))
    if mlt is not None and mlt < 0:
        issues.append(Issue("warn", "min_layer_time_s should be >= 0", "process_defaults.cooling.min_layer_time_s"))
    # Accelerations non-negative
    acc = pd.get("accelerations_mms2") or {}
    for k, v in acc.items():
        vv = _num(v)
        if vv is not None and vv < 0:
            issues.append(Issue("warn", f"Acceleration '{k}' should be >= 0", f"process_defaults.accelerations_mms2.{k}"))

    # General lint: materials checks
    mat_types_present = set()
    for mi, mat in enumerate(materials):
        try:
            mtype = str((mat.get('filament_type') or '')).upper()
        except Exception:
            mtype = ''
        if mtype:
            mat_types_present.add(mtype)
        fd = _num(mat.get('filament_diameter'))
        if fd is not None and all(abs(fd - x) > 0.05 for x in (1.75, 2.85)):
            issues.append(Issue("warn", f"Unusual material filament_diameter: {fd} (typical 1.75 or 2.85)", f"materials[{mi}].filament_diameter"))
        nt = _num(mat.get('nozzle_temperature'))
        bt = _num(mat.get('bed_temperature'))
        if mtype == 'PLA':
            if nt is not None and not (180 <= nt <= 230):
                issues.append(Issue("warn", "PLA nozzle temp usually 180–230 °C", f"materials[{mi}].nozzle_temperature"))
            if bt is not None and not (0 <= bt <= 70):
                issues.append(Issue("warn", "PLA bed temp usually 0–70 °C", f"materials[{mi}].bed_temperature"))
        if mtype == 'PETG':
            if nt is not None and not (220 <= nt <= 260):
                issues.append(Issue("warn", "PETG nozzle temp usually 220–260 °C", f"materials[{mi}].nozzle_temperature"))
            if bt is not None and not (70 <= bt <= 90):
                issues.append(Issue("warn", "PETG bed temp usually 70–90 °C", f"materials[{mi}].bed_temperature"))
        if mtype in ('ABS', 'ASA'):
            if nt is not None and not (230 <= nt <= 260):
                issues.append(Issue("warn", f"{mtype} nozzle temp usually 230–260 °C", f"materials[{mi}].nozzle_temperature"))
            if bt is not None and not (90 <= bt <= 110):
                issues.append(Issue("warn", f"{mtype} bed temp usually 90–110 °C", f"materials[{mi}].bed_temperature"))
        if mtype == 'TPU':
            if nt is not None and not (200 <= nt <= 240):
                issues.append(Issue("warn", "TPU nozzle temp usually 200–240 °C", f"materials[{mi}].nozzle_temperature"))
            if bt is not None and not (30 <= bt <= 60):
                issues.append(Issue("warn", "TPU bed temp usually 30–60 °C", f"materials[{mi}].bed_temperature"))
        # Extrusion multiplier sanity
        em = mat.get('extrusion_multiplier') if isinstance(mat, dict) else None
        try:
            if em is not None and not (0.8 <= float(em) <= 1.2):
                issues.append(Issue("warn", f"Extrusion multiplier unusual: {em} (typical 0.95–1.05)", f"materials[{mi}].extrusion_multiplier"))
        except Exception:
            pass

    # Process speeds lint (if present)
    spd = pd.get('speeds_mms') or {}
    def _spd_warn(key: str, value: Any, max_ok: float, label: str):
        v = _num(value)
        if v is not None and v > max_ok:
            issues.append(Issue("warn", f"{label} unusually high (>{max_ok} mm/s)", f"process_defaults.speeds_mms.{key}"))
    _spd_warn('perimeter', spd.get('perimeter'), 150, 'perimeter speed')
    _spd_warn('infill', spd.get('infill'), 150, 'infill speed')
    _spd_warn('travel', spd.get('travel'), 300, 'travel speed')

    # Retraction vs drive type heuristics
    try:
        drive = str(((extruders or [{}])[0].get('drive') or '')).lower()
    except Exception:
        drive = ''
    retract = _num(pd.get('retract_mm'))
    if retract is not None:
        if drive == 'bowden' and retract < 2.0:
            issues.append(Issue("info", f"Bowden drive typically needs higher retract_mm (>= 2.0); current {retract}", "process_defaults.retract_mm"))
        if drive == 'direct' and retract > 2.0:
            issues.append(Issue("info", f"Direct drive often works with lower retract_mm (<= 2.0); current {retract}", "process_defaults.retract_mm"))

    # Cooling fan policy hints by material type (if any applicable material present)
    cooling = pd.get('cooling') or {}
    try:
        fmax = int(cooling.get('fan_max_percent') or 0)
    except Exception:
        fmax = 0
    if any(m in mat_types_present for m in ('ABS', 'ASA')) and fmax and fmax > 20:
        issues.append(Issue("warn", "ABS/ASA typically use low/no part cooling; reduce fan_max_percent", "process_defaults.cooling.fan_max_percent"))
    if 'PETG' in mat_types_present and fmax and fmax > 60:
        issues.append(Issue("info", "PETG usually benefits from moderate fan (≤60%) to avoid layer adhesion issues", "process_defaults.cooling.fan_max_percent"))
    if 'TPU' in mat_types_present and retract is not None and retract > 3.0:
        issues.append(Issue("warn", "TPU is flexible; consider lower retract_mm (≤3.0) to prevent jams", "process_defaults.retract_mm"))
    return issues
