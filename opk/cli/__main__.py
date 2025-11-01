from __future__ import annotations
import argparse
from pathlib import Path
from ..core import schema as S
from ..core.io import load_json
from ..core.bundle import build_bundle
from ..core.install import plan_install, perform_install
from ..core.gcode import list_hooks as gc_list_hooks, render_sequence as gc_render, render_hooks_with_firmware as gc_render_fw


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

    # install
    ins = sub.add_parser("install", help="Install profiles to Orca presets (with optional backup)")
    ins.add_argument("--src", required=True, help="Source directory with printers/ filaments/ processes/")
    ins.add_argument("--dest", required=True, help="Destination Orca presets directory")
    ins.add_argument("--backup", help="Path to backup ZIP of overwritten files")
    ins.add_argument("--dry-run", action="store_true", help="Compute and print plan without writing files")

    # convert
    cv = sub.add_parser("convert", help="Convert from other formats")
    cv.add_argument("--from", dest="from_fmt", required=True, choices=["cura"], help="Source format")
    cv.add_argument("--in", dest="src", required=True, help="Input file or directory to convert")
    cv.add_argument("--out", dest="out", required=True, help="Output directory (printers)")

    # gcode: list hooks and preview
    gh = sub.add_parser("gcode-hooks", help="List available gcode hooks in a PDL file (YAML/JSON)")
    gh.add_argument("--pdl", required=True, help="Path to PDL file")

    gp = sub.add_parser("gcode-preview", help="Render a gcode hook with variables")
    gp.add_argument("--pdl", required=True, help="Path to PDL file")
    gp.add_argument("--hook", required=True, help="Hook name (e.g., start, before_layer_change, monitor.progress_25)")
    gp.add_argument("--vars", dest="vars_path", help="JSON file with variables for placeholder substitution")

    gv = sub.add_parser("gcode-validate", help="Validate all gcode hooks against provided variables")
    gv.add_argument("--pdl", required=True, help="Path to PDL file")
    gv.add_argument("--vars", dest="vars_path", required=True, help="JSON file with variables for placeholder substitution")

    pv = sub.add_parser("pdl-validate", help="Validate a PDL file against schema and rules")
    pv.add_argument("--pdl", required=True, help="Path to PDL file (YAML/JSON)")
    args = ap.parse_args()
    if args.cmd == "validate": raise SystemExit(cmd_validate(args.paths))
    if args.cmd == "bundle":   raise SystemExit(cmd_bundle(args.src, args.out))
    if args.cmd == "rules":    raise SystemExit(cmd_rules(args.printer, args.filament, args.process))
    if args.cmd == "workspace" and args.subcmd == "init":
        raise SystemExit(cmd_workspace_init(args.root, with_examples=args.with_examples))
    if args.cmd == "install":
        src = Path(args.src); dest = Path(args.dest)
        ops = plan_install(src, dest)
        if args.dry_run:
            for op in ops:
                print(f"[{op.status.upper():6}] {op.category}/{op.name} -> {op.dest}")
            print(f"[SUMMARY] total={len(ops)} add={sum(1 for o in ops if o.status=='add')} update={sum(1 for o in ops if o.status=='update')} same={sum(1 for o in ops if o.status=='same')}")
            raise SystemExit(0)
        res = perform_install(ops, backup_zip=Path(args.backup) if args.backup else None)
        print(f"[INSTALL] written={res['written']} skipped={res['skipped']} total={res['total']}")
        raise SystemExit(0)
    if args.cmd == "convert":
        if args.from_fmt == "cura":
            from ..plugins.converters.cura import convert_cura_input
            out_dir = Path(args.out)
            written = convert_cura_input(Path(args.src), out_dir)
            for w in written:
                print(f"[WROTE] {w}")
            print(f"[SUMMARY] wrote={len(written)}")
            raise SystemExit(0)
    if args.cmd == "gcode-hooks":
        from pathlib import Path as _Path
        import json as _json, yaml as _yaml
        text = _Path(args.pdl).read_text(encoding="utf-8")
        data = _json.loads(text) if args.pdl.endswith((".json", ".JSON")) else _yaml.safe_load(text)
        # Merge machine_control and apply firmware mapping
        gcode = gc_render_fw(data or {})
        hooks = gc_list_hooks(gcode)
        for h in hooks:
            print(h)
        print(f"[SUMMARY] hooks={len(hooks)}")
        raise SystemExit(0)
    if args.cmd == "gcode-preview":
        from pathlib import Path as _Path
        import json as _json, yaml as _yaml
        text = _Path(args.pdl).read_text(encoding="utf-8")
        data = _json.loads(text) if args.pdl.endswith((".json", ".JSON")) else _yaml.safe_load(text)
        gcode = gc_render_fw(data or {})
        seq = None
        if args.hook in gcode:
            seq = gcode.get(args.hook)
        elif isinstance(gcode.get("hooks"), dict) and args.hook in gcode.get("hooks"):
            seq = gcode["hooks"][args.hook]
        if not isinstance(seq, list):
            print(f"[ERROR] Hook not found or not a sequence: {args.hook}")
            raise SystemExit(2)
        vars_obj = {}
        if args.vars_path:
            vars_obj = _json.loads(_Path(args.vars_path).read_text(encoding="utf-8"))
        rendered, missing = gc_render(seq, vars_obj)
        print("\n".join(rendered))
        if missing:
            print(f"\n[WARN] Unresolved placeholders: {', '.join(sorted(missing))}")
        raise SystemExit(0)
    if args.cmd == "gcode-validate":
        from pathlib import Path as _Path
        import json as _json, yaml as _yaml
        text = _Path(args.pdl).read_text(encoding="utf-8")
        data = _json.loads(text) if args.pdl.endswith((".json", ".JSON")) else _yaml.safe_load(text)
        gcode = gc_render_fw(data or {})
        hooks = gc_list_hooks(gcode)
        vars_obj = _json.loads(_Path(args.vars_path).read_text(encoding="utf-8"))
        total_missing = {}
        for h in hooks:
            seq = gcode.get(h) if h in gcode else gcode.get("hooks", {}).get(h)
            if not isinstance(seq, list):
                continue
            _, missing = gc_render(seq, vars_obj)
            if missing:
                total_missing[h] = sorted(missing)
        if total_missing:
            for h, miss in total_missing.items():
                print(f"[MISS] {h}: {', '.join(miss)}")
            print(f"[SUMMARY] hooks={len(hooks)} invalid={len(total_missing)}")
            raise SystemExit(2)
        print(f"[SUMMARY] hooks={len(hooks)} invalid=0")
        raise SystemExit(0)
    if args.cmd == "pdl-validate":
        from pathlib import Path as _Path
        import json as _json, yaml as _yaml
        text = _Path(args.pdl).read_text(encoding="utf-8")
        data = _json.loads(text) if args.pdl.endswith((".json", ".JSON")) else _yaml.safe_load(text)
        # Schema
        try:
            S.validate("pdl", data)
        except Exception as e:
            print(f"[SCHEMA] FAIL: {e}")
            raise SystemExit(2)
        # Rules
        from ..core.rules import validate_pdl, summarize
        issues = validate_pdl(data or {})
        for i in issues:
            print(f"[{i.level.upper()}] {i.path} — {i.message}")
        s = summarize(issues)
        print(f"[SUMMARY] errors={s['error']} warns={s['warn']} infos={s['info']} total={s['total']}")
        raise SystemExit(0 if s['error'] == 0 else 2)

if __name__ == "__main__":
    main()
