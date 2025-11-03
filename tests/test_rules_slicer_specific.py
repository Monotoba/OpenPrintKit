from opk.core.rules import validate_pdl


def test_cura_rectangularize_bed_shape_info():
    pdl = {
        'policies': {'target_slicer': 'cura'},
        'geometry': {
            'bed_shape': [[0,0],[200,0],[150,150],[0,200]]  # non-rectangular
        }
    }
    issues = validate_pdl(pdl)
    assert any('Cura generator uses rectangular bed dimensions' in i.message for i in issues)


def test_prusa_limits_accel_hint():
    pdl = {
        'policies': {'target_slicer': 'prusa'},
        'process_defaults': {'accelerations_mms2': {'perimeter': 1000}}
    }
    issues = validate_pdl(pdl)
    assert any('Consider setting limits.acceleration_max' in i.message for i in issues)


def test_orca_needs_material_info():
    pdl = {
        'policies': {'target_slicer': 'orca'},
        'materials': []
    }
    issues = validate_pdl(pdl)
    assert any('Orca generator expects at least one material' in i.message for i in issues)


def test_ideamaker_speeds_hint():
    pdl = {
        'policies': {'target_slicer': 'ideamaker'},
        'process_defaults': {}
    }
    issues = validate_pdl(pdl)
    assert any('Add speeds_mms (perimeter/infill/travel)' in i.message for i in issues)

