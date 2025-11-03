from pathlib import Path
from opk.plugins.slicers.cura import generate_cura


def test_generate_cura_support_and_patterns(tmp_path: Path):
    pdl = {
        'name': 'CuraSup',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'process_defaults': {
            'layer_height_mm': 0.2,
            'support': 'zigzag',
            'infill_pattern': 'gyroid',
            'walls': 3,
        },
    }
    out = generate_cura(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'support_enable = True' in text
    assert 'support_pattern = zigzag' in text
    assert 'infill_pattern = gyroid' in text
    assert 'wall_line_count = 3' in text

