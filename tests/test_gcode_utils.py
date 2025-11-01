from opk.core.gcode import find_placeholders, render_sequence, list_hooks


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

