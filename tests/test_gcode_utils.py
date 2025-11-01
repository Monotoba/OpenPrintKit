from opk.core.gcode import find_placeholders, render_sequence, list_hooks, apply_machine_control


def test_find_and_render_placeholders():
    seq = [
        "M104 S{nozzle}",
        "M140 S{bed}",
        "; Layer {layer}",
    ]
    found = find_placeholders(seq)
    assert {"nozzle","bed","layer"} <= found
    rendered, missing = render_sequence(seq, {"nozzle": 205, "bed": 60})
    assert "M104 S205" in rendered[0]
    assert "M140 S60" in rendered[1]
    assert "{layer}" in rendered[2]
    assert "layer" in missing


def test_list_hooks_from_gcode():
    g = {
        "start": ["G28"],
        "after_layer_change": ["; A"],
        "hooks": {"monitor.progress_25": ["M117 25%"]}
    }
    hooks = list_hooks(g)
    assert "start" in hooks and "after_layer_change" in hooks and "monitor.progress_25" in hooks


def test_apply_machine_control_injects_start_end():
    pdl = {
        "machine_control": {
            "psu_on_start": True,
            "psu_off_end": True,
            "light_on_start": True,
            "light_off_end": True,
            "rgb_start": {"r": 1, "g": 2, "b": 3},
            "chamber": {"temp": 30, "wait": True},
            "enable_mesh_start": True,
            "z_offset": 0.2,
            "start_custom": ["M117 Hello"],
            "end_custom": ["M117 Bye"]
        }
    }
    g = apply_machine_control(pdl, {})
    s = "\n".join(g.get("start") or [])
    e = "\n".join(g.get("end") or [])
    assert "M80" in s and "M81" in e and "M355 S1" in s and "M355 S0" in e
    assert "M150" in s and "M141 S30" in s and "M191 S30" in s and "M420 S1" in s and "M851 Z0.20" in s
    assert "M117 Hello" in s and "M117 Bye" in e

def test_apply_machine_control_peripherals():
    pdl = {
        "machine_control": {
            "camera": {"use_before_snapshot": True, "command": "M240"},
            "sd_logging": {"enable_start": True, "filename": "log.gco", "stop_at_end": True},
            "fans": {"part_start_percent": 50, "aux_index": 1, "aux_start_percent": 75, "off_at_end": True}
        }
    }
    g = apply_machine_control(pdl, {})
    assert "M240" in ("\n".join(g.get("before_snapshot") or []))
    s = "\n".join(g.get("start") or [])
    e = "\n".join(g.get("end") or [])
    assert "M928 log.gco" in s and "M29" in e
    assert "M106 S" in s and "M106 P1 S" in s and "M107" in e
