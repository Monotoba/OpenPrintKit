from opk.core.rules import validate_pdl


def test_materials_and_retract_lint():
    pdl = {
        'firmware': 'marlin',
        'extruders': [{'nozzle_diameter': 0.4, 'drive': 'bowden'}],
        'materials': [
            {'name': 'PLA', 'filament_type': 'PLA', 'filament_diameter': 2.2, 'nozzle_temperature': 240, 'bed_temperature': 90},
        ],
        'process_defaults': {
            'layer_height_mm': 0.2,
            'speeds_mms': {
                'perimeter': 200,
                'infill': 180,
                'travel': 350,
            },
            'retract_mm': 1.0,
        }
    }
    issues = validate_pdl(pdl)
    msgs = [i.message for i in issues]
    # Unusual filament diameter
    assert any('Unusual material filament_diameter' in m for m in msgs)
    # PLA temps out of range
    assert any('PLA nozzle temp usually' in m for m in msgs)
    assert any('PLA bed temp usually' in m for m in msgs)
    # Speeds warnings
    assert any('perimeter speed unusually high' in m for m in msgs)
    assert any('infill speed unusually high' in m for m in msgs)
    assert any('travel speed unusually high' in m for m in msgs)
    # Retract vs drive hint
    assert any('Bowden drive typically needs higher retract_mm' in m for m in msgs)


def test_abs_petg_tpu_policies():
    pdl = {
        'firmware': 'marlin',
        'extruders': [{'nozzle_diameter': 0.4, 'drive': 'direct'}],
        'materials': [
            {'name': 'ABS', 'filament_type': 'ABS', 'nozzle_temperature': 200, 'bed_temperature': 60},
            {'name': 'PETG', 'filament_type': 'PETG', 'nozzle_temperature': 210, 'bed_temperature': 50},
            {'name': 'TPU', 'filament_type': 'TPU'},
        ],
        'process_defaults': {
            'cooling': { 'fan_max_percent': 80 },
            'retract_mm': 4.0,
        }
    }
    issues = validate_pdl(pdl)
    msgs = [i.message for i in issues]
    # ABS temps out of range
    assert any('ABS nozzle temp usually' in m for m in msgs)
    assert any('ABS bed temp usually' in m for m in msgs)
    # PETG temps/info
    assert any('PETG nozzle temp usually' in m for m in msgs)
    # ABS fan policy
    assert any('ABS/ASA typically use low/no part cooling' in m for m in msgs)
    # TPU retract hint
    assert any('TPU is flexible; consider lower retract_mm' in m for m in msgs)
