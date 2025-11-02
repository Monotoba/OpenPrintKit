from __future__ import annotations
import json, zipfile, time
from pathlib import Path
from typing import Dict, Any
from . import schema as S

def build_bundle(src_dir: Path, out_path: Path) -> Path:
    printers  = sorted((src_dir / "printers").glob("*.json"), key=lambda p: p.name)
    filaments = sorted((src_dir / "filaments").glob("*.json"), key=lambda p: p.name)
    processes = sorted((src_dir / "processes").glob("*.json"), key=lambda p: p.name)
    assert printers and filaments and processes, "Missing profiles in src_dir"

    manifest: Dict[str, Any] = {
        "generator": "opk.bundle",
        "printer_count": len(printers),
        "filament_count": len(filaments),
        "process_count": len(processes),
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # before writing each file, validate against the correct schema
    KIND_MAP = {
      "printers": "printer",
      "filaments": "filament",
      "processes": "process",
    }

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
      for rel, files in (("printers", printers), ("filaments", filaments), ("processes", processes)):
        for p in files:
          data = json.loads(p.read_text(encoding="utf-8"))
          kind = KIND_MAP[rel]  # explicit mapping (avoids 'processe')
          S.validate(kind, data)
          zf.writestr(f"{rel}/{p.name}", json.dumps(data, indent=2))
      zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    S.validate("bundle", manifest)
    return out_path


def build_profile_bundle(files: Dict[str, Path], out_path: Path, slicer: str) -> Path:
    """Bundle generated slicer profile files into a simple ZIP with a manifest.

    files: mapping name->path from a generator (e.g., {'profile': Path(...)})
    slicer: one of 'cura', 'prusa', 'ideamaker'
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, Any] = {
        'generator': 'opk.profile-bundle',
        'slicer': slicer,
        'files': sorted([p.name for p in files.values()])
    }
    import zipfile, json
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for key, p in files.items():
            if Path(p).exists():
                zf.write(p, arcname=Path(p).name)
        zf.writestr('manifest.json', json.dumps(manifest, indent=2))
    return out_path
