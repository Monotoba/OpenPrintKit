from pathlib import Path

from opk.plugins.slicers.kisslicer import generate_kisslicer


def test_generate_kisslicer_escapes_multiline_gcode(tmp_path: Path):
    pdl = {
        "name": "Test KISSlicer",
        "gcode": {
            "start": ["G28", "G1 Z5"],
            "end": ["M104 S0", "M84"],
        },
    }

    profile = generate_kisslicer(pdl, tmp_path)["profile"]
    text = profile.read_text(encoding="utf-8")

    assert "start_gcode = G28\\nG1 Z5" in text
    assert "end_gcode = M104 S0\\nM84" in text
