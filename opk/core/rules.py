from __future__ import annotations
from typing import Dict, List, Any
class Issue:
    def __init__(self, level: str, message: str, path: str=""):
        self.level, self.message, self.path = level, message, path
    def as_dict(self): return {"level": self.level, "message": self.message, "path": self.path}

def validate_process(proc: Dict[str, Any], printer: Dict[str, Any] | None=None) -> List[Issue]:
    issues: List[Issue] = []
    nozzle = (printer or {}).get("nozzle_diameter")
    for key in ("layer_height","first_layer_height"):
        v = proc.get(key)
        if nozzle and v and float(v) > 0.8 * float(nozzle):
            issues.append(Issue("warn", f"{key} > 80% of nozzle", key))
    return issues
