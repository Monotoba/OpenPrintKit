from pathlib import Path
from opk.plugins.slicers.prusa import generate_prusa


def test_generate_prusa_with_limits_accel(tmp_path: Path):
    pdl = {
        'name': 'PrusaLimits',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'limits': {'acceleration_max': 2500},
    }
    out = generate_prusa(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'max_print_acceleration = 2500' in text
    assert 'max_travel_acceleration = 2500' in text

