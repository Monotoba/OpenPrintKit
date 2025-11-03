from pathlib import Path
from opk.plugins.slicers.superslicer import generate_superslicer


def test_generate_superslicer_fill_density(tmp_path: Path):
    pdl = {
        'name': 'SSFill',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'process_defaults': {
            'infill_percent': 30,
        },
    }
    out = generate_superslicer(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'fill_density = 30' in text

