from pathlib import Path
import yaml
from opk.core import schema as S


def test_pdl_examples_validate():
    examples = (Path(__file__).resolve().parents[1] / "pdl-spec" / "examples").glob("*.yaml")
    count = 0
    for p in examples:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        S.validate("pdl", data)
        count += 1
    assert count >= 3

