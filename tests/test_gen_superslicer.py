from pathlib import Path
from opk.plugins.slicers.superslicer import generate_superslicer


def test_generate_superslicer(tmp_path: Path):
    pdl = {
        'name': 'TestSS',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
    }
    out = generate_superslicer(pdl, tmp_path)
    ini = out['profile']
    text = ini.read_text(encoding='utf-8')
    assert 'bed_shape' in text and 'nozzle_diameter' in text

