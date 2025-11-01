from opk.core.gcode import render_hooks_with_firmware


def test_openprinttag_injection():
    pdl = {
        "open_print_tag": {
            "id": "abc123",
            "url": "https://example.com/printer",
            "manufacturer": "OPK",
            "model": "Test",
        }
    }
    hooks = render_hooks_with_firmware(pdl)
    start = hooks.get("start") or []
    assert any(str(s).startswith(";BEGIN:OPENPRINTTAG") for s in start)
    assert any("\"id\": \"abc123\"" in s for s in start)

