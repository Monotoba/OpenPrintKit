from pathlib import Path
from opk.cli.__main__ import main as cli_main
import sys, json, pytest


def run(argv):
    old = sys.argv[:]
    try:
        sys.argv = argv
        with pytest.raises(SystemExit) as e:
            cli_main()
        return e.value.code
    finally:
        sys.argv = old


def test_convert_prusa_ini(tmp_path: Path):
    ini = tmp_path / 'test.ini'
    ini.write_text('[printer:TestPrusa]\nbed_shape = 0x0,220x0,220x220,0x220\nnozzle_diameter = 0.4\nstart_gcode = G28\\nG1 X0\nend_gcode = M84\n\n[filament:PLA]\nfilament_diameter = 1.75\n', encoding='utf-8')
    outd = tmp_path / 'out'
    code = run(['opk', 'convert', '--from', 'prusa', '--in', str(ini), '--out', str(outd)])
    assert code == 0
    outs = list(outd.glob('*.json'))
    assert outs
    data = json.loads(outs[0].read_text(encoding='utf-8'))
    assert data['type'] == 'printer' and data['build_volume'][0] == 220

