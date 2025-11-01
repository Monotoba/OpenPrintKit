from opk.core.gcode import render_sequence


def test_render_dotted_and_array_vars():
    seq = [
        "; {printer.name}",
        "M118 Dia {filament_diameter[0]}"
    ]
    vars = {"printer": {"name": "MK3S"}, "filament_diameter": [1.75, 2.85]}
    out, missing = render_sequence(seq, vars)
    assert "; MK3S" in out[0]
    assert "1.75" in out[1]
    assert not missing

