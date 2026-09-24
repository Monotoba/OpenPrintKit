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


def test_grbl_exhaust_mapping():
    pdl = {
        "firmware": "grbl",
        "machine_control": {
            "exhaust": {"enable_start": True, "off_at_end": True}
        },
    }

    hooks = render_hooks_with_firmware(pdl)

    assert hooks["start"][-1] == "M8"
    assert hooks["end"][-1] == "M9"


def test_linuxcnc_exhaust_mapping():
    pdl = {
        "firmware": "linuxcnc",
        "machine_control": {
            "exhaust": {"enable_start": True, "off_at_end": True}
        },
    }

    hooks = render_hooks_with_firmware(pdl)

    assert hooks["start"][-1] == "M7"
    assert hooks["end"][-1] == "M9"
