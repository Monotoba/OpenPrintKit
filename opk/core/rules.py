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
    return issues
