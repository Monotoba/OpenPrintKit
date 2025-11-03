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

