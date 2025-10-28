from pathlib import Path
from opk.core.bundle import build_bundle
def test_bundle(tmp_path: Path):
    root = Path(__file__).resolve().parents[1] / "examples"
    out  = tmp_path / "test.orca_printer"
    build_bundle(root, out)
    assert out.exists()
