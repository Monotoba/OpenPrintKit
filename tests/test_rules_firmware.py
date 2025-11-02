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


def test_rules_rrf_sd_logging_and_named_pin():
    pdl = {
        'firmware': 'rrf',
        'machine_control': {
            'sd_logging': { 'enable_start': True, 'filename': 'log file.gco' },
            'exhaust': { 'pin': 10 },
            'fans': { 'aux_index': 1, 'aux_start_percent': 50 }
        }
    }
    issues = validate_pdl(pdl)
    msgs = [i.message for i in issues]
    assert any('RRF: SD logging uses M929' in m for m in msgs)
    assert any('filename contains spaces' in m for m in msgs)
    assert any('prefer named pins' in m for m in msgs)
    assert any('Aux fan configured without off_at_end' in m for m in msgs)


def test_rules_marlin_exhaust_string_pin_warn():
    pdl = {
        'firmware': 'marlin',
        'machine_control': { 'exhaust': { 'pin': 'out1' } }
    }
    issues = validate_pdl(pdl)
    assert any(i.level == 'warn' and 'Marlin M42 expects numeric pin' in i.message for i in issues)
