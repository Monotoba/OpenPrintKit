from pathlib import Path
from opk.plugins.slicers.bambu import generate_bambu


def test_generate_bambu_fill_density(tmp_path: Path):
    pdl = {
        'name': 'BambuFill',
        'geometry': {'bed_shape': [[0,0],[256,0],[256,256],[0,256]], 'z_height': 256},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'process_defaults': {
            'infill_percent': 18,
        },
    }
    out = generate_bambu(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'fill_density = 18' in text

