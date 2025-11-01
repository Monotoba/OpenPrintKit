from __future__ import annotations
import argparse
from pathlib import Path
from ..core import schema as S
from ..core.io import load_json
from ..core.bundle import build_bundle


def cmd_workspace_init(root, with_examples: bool):
  from pathlib import Path
  from ..workspace.scaffold import init_workspace
  p = init_workspace(Path(root), with_examples=with_examples)
  print(f"[OK] Initialized workspace at: {p}")
  return 0


def cmd_rules(printer: str | None, filament: str | None, process: str | None):
  from ..core.io import load_json
  from ..core.rules import validate_printer, validate_filament, validate_process, summarize
  pr = load_json(printer) if printer else {}
  fi = load_json(filament) if filament else {}
  ps = load_json(process) if process else {}
  ip = validate_printer(pr) if pr else []
  ifi = validate_filament(fi) if fi else []
  ips = validate_process(ps, pr if pr else None) if ps else []
  for label, issues in (("printer", ip), ("filament", ifi), ("process", ips)):
    for i in issues:
      print(f"[{i.level.upper():5}] {label}:{i.path} — {i.message}")
  s = summarize(ip, ifi, ips)
  print(f"[SUMMARY] errors={s['error']} warns={s['warn']} infos={s['info']} total={s['total']}")
  return 0 if s["error"] == 0 else 2


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
    # validate
    v = sub.add_parser("validate", help="Validate profile JSON files against schema")
    v.add_argument("paths", nargs="+", help="Path(s) to JSON profile files")

    # bundle
    b = sub.add_parser("bundle", help="Bundle profiles into an .orca_printer archive")
    b.add_argument("--in", dest="src", required=True, help="Source directory with printers/ filaments/ processes/")
    b.add_argument("--out", required=True, help="Output .orca_printer path")

    # rules
    r = sub.add_parser("rules", help="Run rule-based checks across printer/filament/process")
    r.add_argument("--printer", help="Path to printer profile JSON", default=None)
    r.add_argument("--filament", help="Path to filament profile JSON", default=None)
    r.add_argument("--process", help="Path to process profile JSON", default=None)

    # workspace
    w = sub.add_parser("workspace", help="Workspace utilities")
    wsub = w.add_subparsers(dest="subcmd", required=True)
    wi = wsub.add_parser("init", help="Initialize a workspace directory")
    wi.add_argument("root", help="Target workspace directory to create or reuse")
    ex_group = wi.add_mutually_exclusive_group()
    ex_group.add_argument("--examples", dest="with_examples", action="store_true", help="Include example profiles (default)")
    ex_group.add_argument("--no-examples", dest="with_examples", action="store_false", help="Do not include example profiles")
    wi.set_defaults(with_examples=True)
    args = ap.parse_args()
    if args.cmd == "validate": raise SystemExit(cmd_validate(args.paths))
    if args.cmd == "bundle":   raise SystemExit(cmd_bundle(args.src, args.out))
    if args.cmd == "rules":    raise SystemExit(cmd_rules(args.printer, args.filament, args.process))
    if args.cmd == "workspace" and args.subcmd == "init":
        raise SystemExit(cmd_workspace_init(args.root, with_examples=args.with_examples))

if __name__ == "__main__":
    main()
