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


def test_convert_ideamaker_cfg(tmp_path: Path):
    cfg = tmp_path / 'test.cfg'
    cfg.write_text('machineWidth=220\nmachineDepth=220\nmachineHeight=220\nnozzleDiameter=0.4\nfilamentDiameter=1.75\n', encoding='utf-8')
    outd = tmp_path / 'out'
    code = run(['opk', 'convert', '--from', 'ideamaker', '--in', str(cfg), '--out', str(outd)])
    assert code == 0
    outs = list(outd.glob('*.json'))
    assert outs
    data = json.loads(outs[0].read_text(encoding='utf-8'))
    assert data['build_volume'] == [220,220,220]

