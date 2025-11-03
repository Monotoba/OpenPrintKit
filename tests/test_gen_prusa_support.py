from pathlib import Path
from opk.plugins.slicers.prusa import generate_prusa


def test_generate_prusa_support_and_patterns(tmp_path: Path):
    pdl = {
        'name': 'PrusaSup',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'process_defaults': {
            'speeds_mms': {'perimeter': 40},
            'support': 'grid',
            'infill_pattern': 'gyroid',
            'walls': 3,
        },
    }
    out = generate_prusa(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'support_material = 1' in text
    assert 'support_material_pattern = grid' in text
    assert 'fill_pattern = gyroid' in text
    assert 'perimeters = 3' in text

