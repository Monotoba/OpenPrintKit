from pathlib import Path
from opk.plugins.slicers.prusa import generate_prusa


def test_generate_prusa_with_process_defaults(tmp_path: Path):
    pdl = {
        'name': 'PrusaProc',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 210, 'bed_temperature': 65}],
        'process_defaults': {
            'layer_height_mm': 0.18,
            'first_layer_mm': 0.27,
            'speeds_mms': {'perimeter': 42, 'infill': 58, 'travel': 155},
            'adhesion': 'brim',
        },
    }
    out = generate_prusa(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'layer_height = 0.18' in text
    assert 'first_layer_height = 0.27' in text
    assert 'perimeter_speed = 42' in text and 'infill_speed = 58' in text and 'travel_speed = 155' in text
    assert 'brim_width = 5' in text

