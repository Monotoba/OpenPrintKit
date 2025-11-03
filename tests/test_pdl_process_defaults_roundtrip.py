import pytest


def test_pdl_process_defaults_roundtrip():
    try:
        from PySide6.QtWidgets import QApplication
    except Exception:
        pytest.skip("PySide6 not available")
    from opk.ui.pdl_editor import PDLForm

    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    app = QApplication.instance() or QApplication([])
    w = PDLForm()
    pdl_in = {
        'pdl_version': '1.0',
        'name': 'RT',
        'geometry': {'bed_shape': [[0,0],[200,0],[200,200],[0,200]], 'z_height': 200},
        'extruders': [{'nozzle_diameter': 0.4}],
        'process_defaults': {
            'layer_height_mm': 0.21,
            'first_layer_mm': 0.29,
            'speeds_mms': {'perimeter': 41, 'infill': 57, 'travel': 152, 'external_perimeter': 35, 'top': 28, 'bottom': 28},
            'retract_mm': 0.8,
            'retract_speed_mms': 40,
            'adhesion': 'brim',
            'extrusion_multiplier': 1.04,
            'cooling': {'min_layer_time_s': 6, 'fan_min_percent': 25, 'fan_max_percent': 100, 'fan_always_on': True},
            'accelerations_mms2': {'perimeter': 1000, 'infill': 1200, 'external_perimeter': 800, 'top': 600, 'bottom': 600, 'travel': 1500},
        },
    }
    w.load_pdl(pdl_in)
    out = w.dump_pdl()
    pd = out.get('process_defaults', {})
    assert pd.get('layer_height_mm') == 0.21
    assert pd.get('first_layer_mm') == 0.29
    assert pd.get('speeds_mms', {}).get('perimeter') == 41
    assert pd.get('retract_mm') == pytest.approx(0.8)
    assert pd.get('retract_speed_mms') == 40
    assert pd.get('adhesion') == 'brim'
    assert pd.get('extrusion_multiplier') == pytest.approx(1.04)
    cool = pd.get('cooling', {})
    assert cool.get('min_layer_time_s') == 6 and cool.get('fan_min_percent') == 25 and cool.get('fan_max_percent') == 100 and cool.get('fan_always_on') is True
    acc = pd.get('accelerations_mms2', {})
    assert acc.get('perimeter') == 1000 and acc.get('travel') == 1500
