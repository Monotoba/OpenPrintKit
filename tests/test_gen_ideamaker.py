from pathlib import Path
from opk.plugins.slicers.ideamaker import generate_ideamaker


def test_generate_ideamaker(tmp_path: Path):
    pdl = {
        'name': 'TestIM',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
    }
    out = generate_ideamaker(pdl, tmp_path)
    cfg = out['profile']
    text = cfg.read_text(encoding='utf-8')
    assert 'machineWidth' in text and 'nozzleDiameter' in text

