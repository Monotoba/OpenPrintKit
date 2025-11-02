from opk.core.rules import validate_pdl, summarize


def test_rules_grbl_exhaust_guidance():
    pdl = {
        'firmware': 'grbl',
        'machine_control': {
            'exhaust': {
                'enable_start': True,
                # off_at_end intentionally omitted
                'pin': 10,
            }
        }
    }
    issues = validate_pdl(pdl)
    msgs = [i.message for i in issues]
    assert any('GRBL/LinuxCNC exhaust maps to coolant' in m for m in msgs)
    assert any('ignores raw pin control' in m for m in msgs)


def test_rules_klipper_camera_info():
    pdl = {
        'firmware': 'klipper',
        'machine_control': {
            'camera': { 'use_before_snapshot': True, 'command': 'M240' }
        }
    }
    issues = validate_pdl(pdl)
    assert any(i.level == 'info' and 'mapped to' in i.message for i in issues)

