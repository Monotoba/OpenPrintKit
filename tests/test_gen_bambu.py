from pathlib import Path
from opk.plugins.slicers.bambu import generate_bambu


def test_generate_bambu(tmp_path: Path):
    pdl = {
        'name': 'TestBambu',
        'geometry': {'bed_shape': [[0,0],[256,0],[256,256],[0,256]], 'z_height': 256},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
    }
    out = generate_bambu(pdl, tmp_path)
    ini = out['profile']
    text = ini.read_text(encoding='utf-8')
    assert 'printer:' in text and 'start_gcode' in text

