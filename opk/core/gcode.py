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


def _render_line(line: str, variables: Dict[str, object]) -> Tuple[str, Set[str]]:
    missing: Set[str] = set()

    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in variables:
            return str(variables[key])
        missing.add(key)
        return m.group(0)  # leave placeholder as-is

    return PLACEHOLDER_RE.sub(repl, line), missing


def render_sequence(seq: Iterable[str], variables: Dict[str, object]) -> Tuple[List[str], Set[str]]:
    out: List[str] = []
    missing: Set[str] = set()
    for line in seq:
        r, miss = _render_line(line, variables)
        out.append(r)
        missing |= miss
    return out, missing

