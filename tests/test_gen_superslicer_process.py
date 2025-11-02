from pathlib import Path
from opk.plugins.slicers.superslicer import generate_superslicer


def test_generate_superslicer_with_process_defaults(tmp_path: Path):
    pdl = {
        'name': 'SSProc',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 210, 'bed_temperature': 65}],
        'process_defaults': {
            'layer_height_mm': 0.21,
            'first_layer_mm': 0.29,
            'speeds_mms': {'perimeter': 41, 'infill': 57, 'travel': 152},
        },
    }
    out = generate_superslicer(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'layer_height = 0.21' in text
    assert 'first_layer_height = 0.29' in text
    assert 'perimeter_speed = 41' in text and 'infill_speed = 57' in text and 'travel_speed = 152' in text

