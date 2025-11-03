from pathlib import Path
from opk.plugins.slicers.prusa import generate_prusa


def test_generate_prusa_fill_density(tmp_path: Path):
    pdl = {
        'name': 'PrusaFill',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'process_defaults': {
            'infill_percent': 22,
        },
    }
    out = generate_prusa(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'fill_density = 22' in text

