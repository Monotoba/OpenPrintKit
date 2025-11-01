from pathlib import Path
from opk.plugins.slicers.cura import generate_cura


def test_generate_cura(tmp_path: Path):
    pdl = {
        'name': 'TestCura',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
    }
    out = generate_cura(pdl, tmp_path)
    cfg = out['profile']
    text = cfg.read_text(encoding='utf-8')
    assert 'machine_width' in text and 'layer_height' in text

