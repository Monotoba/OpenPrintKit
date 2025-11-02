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


def test_convert_superslicer_ini(tmp_path: Path):
    ini = tmp_path / 'test.ini'
    ini.write_text('[printer:SS]\nbed_shape = 0x0,200x0,200x200,0x200\nnozzle_diameter = 0.4\n\n[filament:PLA]\nfilament_diameter = 1.75\n', encoding='utf-8')
    outd = tmp_path / 'out'
    code = run(['opk', 'convert', '--from', 'superslicer', '--in', str(ini), '--out', str(outd)])
    assert code == 0
    outs = list(outd.glob('*.json'))
    assert outs and 'SS' in outs[0].name

