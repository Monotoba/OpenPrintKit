import sys
from pathlib import Path
import pytest


def run_main(argv):
    from opk.cli.__main__ import main
    old = sys.argv[:]
    try:
        sys.argv = argv
        with pytest.raises(SystemExit) as e:
            main()
        return e.value.code
    finally:
        sys.argv = old


def test_cli_gen_prusa_with_acc_overrides(tmp_path: Path):
    # Minimal PDL
    pdl = tmp_path / "pdl.yaml"
    pdl.write_text(
        """
        pdl_version: 1.0
        id: test
        name: Test
        firmware: marlin
        kinematics: cartesian
        geometry:
          bed_shape: [[0,0],[200,0],[200,200],[0,200]]
          z_height: 200
        extruders: [{ nozzle_diameter: 0.4 }]
        """,
        encoding="utf-8",
    )
    outd = tmp_path / "out"
    code = run_main([
        "opk", "gen", "--pdl", str(pdl), "--slicer", "prusa", "--out", str(outd),
        "--acc-perimeter", "1234", "--acc-infill", "1500", "--acc-external", "900",
    ])
    assert code == 0
    # Find generated ini
    ini = next((outd / "prusa").glob("*.ini"))
    text = ini.read_text(encoding="utf-8")
    assert "perimeter_acceleration = 1234" in text
    assert "infill_acceleration = 1500" in text
    assert "external_perimeter_speed" in text or "perimeter_speed" in text

