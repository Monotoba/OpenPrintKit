from __future__ import annotations
import json
import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal

Category = Literal["printers", "filaments", "processes"]


@dataclass
class InstallOp:
    category: Category
    name: str
    src: Path
    dest: Path
    status: Literal["add", "update", "same"]


def _normalized_json_bytes(p: Path) -> bytes:
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        # fallback to raw bytes to avoid crashing; still allow copy
        return p.read_bytes()
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), indent=2).encode(
        "utf-8"
    )


def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def plan_install(src_dir: Path, dest_dir: Path) -> List[InstallOp]:
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    ops: List[InstallOp] = []
    for category in ("printers", "filaments", "processes"):
        sdir = src_dir / category
        if not sdir.exists():
            # skip missing categories; GUI/CLI can handle empty plan as warning
            continue
        for sp in sorted(sdir.glob("*.json"), key=lambda p: p.name):
            dp = dest_dir / category / sp.name
            sb = _normalized_json_bytes(sp)
            if not dp.exists():
                status = "add"
            else:
                db = _normalized_json_bytes(dp)
                status = "same" if _hash_bytes(sb) == _hash_bytes(db) else "update"
            ops.append(InstallOp(category=category, name=sp.name, src=sp, dest=dp, status=status))
    return ops


def perform_install(ops: List[InstallOp], backup_zip: Path | None = None) -> dict:
    # Create backup of files that will be overwritten
    if backup_zip:
        backup_zip = Path(backup_zip)
        backup_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(backup_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for op in ops:
                if op.status == "update" and op.dest.exists():
                    # write with relative path under category/
                    arcname = f"{op.category}/{op.dest.name}"
                    zf.write(op.dest, arcname)

    # Apply operations
    written = 0
    skipped = 0
    for op in ops:
        if op.status in ("add", "update"):
            op.dest.parent.mkdir(parents=True, exist_ok=True)
            op.dest.write_bytes(_normalized_json_bytes(op.src))
            written += 1
        else:
            skipped += 1

    return {"written": written, "skipped": skipped, "total": len(ops)}

