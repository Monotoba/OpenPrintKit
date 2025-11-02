from pathlib import Path
from opk.plugins.slicers.cura import generate_cura


def test_generate_cura_with_limits_accel_jerk(tmp_path: Path):
    pdl = {
        'name': 'CuraLimits',
        'geometry': {'bed_shape': [[0,0],[200,0],[200,200],[0,200]], 'z_height': 200},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'filament_diameter': 1.75, 'nozzle_temperature': 205, 'bed_temperature': 60}],
        'limits': {'acceleration_max': 3000, 'jerk_max': 9},
    }
    out = generate_cura(pdl, tmp_path)
    text = out['profile'].read_text(encoding='utf-8')
    assert 'acceleration_enabled = True' in text
    assert 'acceleration_print = 3000' in text
    assert 'jerk_enabled = True' in text
    assert 'jerk_travel = 9' in text

