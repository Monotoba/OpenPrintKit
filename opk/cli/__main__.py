from __future__ import annotations
import argparse
from pathlib import Path
from ..core import schema as S
from ..core.io import load_json
from ..core.bundle import build_bundle

def cmd_validate(paths):
    ok = True
    for p in paths:
        obj = load_json(p)
        kind = obj.get("type")
        try:
            S.validate(kind, obj)
        except Exception as e:
            ok = False; print(f"[FAIL] {p}: {e}")
        else:
            print(f"[ OK ] {p}")
    return 0 if ok else 1

def cmd_bundle(src_dir, out):
    out = Path(out)
    if not out.suffix: out = out.with_suffix(".orca_printer")
    build_bundle(Path(src_dir), out)
    print(f"[WROTE] {out}")
    return 0

def main():
    ap = argparse.ArgumentParser(prog="opk", description="OpenPrintKit CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("paths", nargs="+")
    b = sub.add_parser("bundle");  b.add_argument("--in", dest="src", required=True); b.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "validate": raise SystemExit(cmd_validate(args.paths))
    if args.cmd == "bundle":   raise SystemExit(cmd_bundle(args.src, args.out))

if __name__ == "__main__":
    main()
