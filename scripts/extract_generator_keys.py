#!/usr/bin/env python3
from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import Dict, Set

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / 'opk' / 'plugins' / 'slicers'
DOC = ROOT / 'docs' / 'exact-generator-keys.md'


def extract_string_keys_from_source(text: str) -> Set[str]:
    keys: Set[str] = set()
    # Find "key =" patterns inside string/f-string literals in a broad way
    # This is heuristic but works for our generator style (e.g., 'key = {value}')
    for m in re.finditer(r"['\"]([A-Za-z0-9_]+)\s*=\s", text):
        keys.add(m.group(1))
    return keys


def extract_dict_keys_from_ast(text: str) -> Set[str]:
    keys: Set[str] = set()
    try:
        tree = ast.parse(text)
    except Exception:
        return keys
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys or []:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
    return keys


def collect_keys_for_file(path: Path) -> Set[str]:
    text = path.read_text(encoding='utf-8')
    keys = set()
    keys.update(extract_string_keys_from_source(text))
    keys.update(extract_dict_keys_from_ast(text))
    return keys


def main() -> int:
    modules: Dict[str, Set[str]] = {}
    for p in sorted(PLUGINS_DIR.glob('*.py')):
        if p.name == '__init__.py':
            continue
        mod = p.stem  # e.g., 'orca', 'prusa'
        modules[mod] = collect_keys_for_file(p)
    # Write doc
    lines = ["# Exact Generator Keys (Parsed from string literals and dict keys)", ""]
    for mod in sorted(modules.keys()):
        keys = sorted(k for k in modules[mod] if k and not k.startswith('#'))
        lines.append(f"## {mod}.py")
        for k in keys:
            lines.append(f"- {k}")
        lines.append("")
    DOC.write_text("\n".join(lines).rstrip() + "\n", encoding='utf-8')
    print(f"[WROTE] {DOC}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

