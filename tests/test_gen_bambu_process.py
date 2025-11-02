from pathlib import Path
from opk.plugins.slicers.bambu import generate_bambu


def test_generate_bambu_with_process_defaults(tmp_path: Path):
    pdl = {
        'name': 'BambuProc',
        'geometry': {'bed_shape': [[0,0],[256,0],[256,256],[0,256]], 'z_height': 256},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 210, 'bed_temperature': 65}],
        'process_defaults': {
            'layer_height_mm': 0.21,
            'first_layer_mm': 0.29,
            'speeds_mms': {'perimeter': 41, 'infill': 57, 'travel': 152},
        },
    }
    out = generate_bambu(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'layer_height = 0.21' in text
    assert 'first_layer_height = 0.29' in text
    assert 'perimeter_speed = 41' in text and 'infill_speed = 57' in text and 'travel_speed = 152' in text

