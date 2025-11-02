from pathlib import Path
from opk.plugins.slicers.cura import generate_cura


def test_generate_cura_with_process_defaults(tmp_path: Path):
    pdl = {
        'name': 'CuraProc',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 210, 'bed_temperature': 65}],
        'process_defaults': {
            'layer_height_mm': 0.22,
            'first_layer_mm': 0.30,
            'speeds_mms': {'perimeter': 45, 'infill': 55, 'travel': 160},
            'retract_mm': 0.8,
            'retract_speed_mms': 40,
            'adhesion': 'brim',
        },
    }
    out = generate_cura(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'initial_layer_height = 0.3' in text
    assert 'layer_height = 0.22' in text
    assert 'speed_travel = 160' in text
    assert 'retraction_enable = 1' in text
    assert 'retraction_amount = 0.80' in text
    assert 'adhesion_type = brim' in text

