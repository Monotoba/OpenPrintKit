from pathlib import Path
from opk.plugins.slicers.superslicer import generate_superslicer


def test_generate_superslicer_support_and_patterns(tmp_path: Path):
    pdl = {
        'name': 'SSSup',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'process_defaults': {
            'speeds_mms': {'perimeter': 40},
            'support': True,
            'infill_pattern': 'rectilinear',
            'walls': 2,
        },
    }
    out = generate_superslicer(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'support_material = 1' in text
    assert 'fill_pattern = rectilinear' in text
    assert 'perimeters = 2' in text

