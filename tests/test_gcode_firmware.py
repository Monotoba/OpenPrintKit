from opk.core.gcode import render_hooks_with_firmware


def test_klipper_camera_mapping():
    pdl = {
        "firmware": "klipper",
        "machine_control": {
            "camera": {"use_before_snapshot": True, "command": "M240"}
        }
    }
    hooks = render_hooks_with_firmware(pdl)
    seq = hooks.get("before_snapshot") or []
    assert any("TIMELAPSE_TAKE_FRAME" in s for s in seq)

