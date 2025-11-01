from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import json


def find_project_file(start: Path) -> Path | None:
    start = start.resolve()
    for p in [start] + list(start.parents):
        for name in ('.opk-project.yaml', '.opk-project.yml', '.opk-project.json'):
            cand = p / name
            if cand.exists():
                return cand
    return None


def load_project_config(p: Path) -> Dict[str, Any]:
    text = p.read_text(encoding='utf-8')
    if p.suffix.lower() == '.json':
        return json.loads(text)
    else:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}


def merge_policies(pdl: Dict[str, Any], proj: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(pdl or {})
    pol = dict(out.get('policies') or {})
    ppol = proj.get('policies') or {}
    # shallow merge
    for k, v in ppol.items():
        cur = dict(pol.get(k) or {})
        cur.update(v or {})
        pol[k] = cur
    if pol:
        out['policies'] = pol
    return out

