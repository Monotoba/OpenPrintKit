from opk.core.rules import validate_pdl


def test_rrf_aux_index_and_named_pins():
    pdl = {
        'firmware': 'rrf',
        'machine_control': {
            'fans': { 'aux_start_percent': 50, 'off_at_end': False },
            'aux_outputs': [ {'label': 'Aux1', 'pin': 10} ],
            'exhaust': { 'pin': 5 }
        }
    }
    issues = validate_pdl(pdl)
    msgs = [i.message for i in issues]
    # aux_start without aux_index
    assert any('aux_start_percent set without aux_index' in m for m in msgs)
    # prefer named pins for aux_outputs and exhaust
    assert any('prefer named pins' in m and 'aux_outputs' in i.path for i,m in zip(issues, msgs))
    assert any('prefer named pins' in m and 'exhaust.pin' in i.path for i,m in zip(issues, msgs))


def test_marlin_mesh_enable_z_offset_hint():
    pdl = {
        'firmware': 'marlin',
        'machine_control': {
            'enable_mesh_start': True,
            'z_offset': 0
        }
    }
    issues = validate_pdl(pdl)
    assert any('mesh enabled; consider setting probe Z offset' in i.message for i in issues)
