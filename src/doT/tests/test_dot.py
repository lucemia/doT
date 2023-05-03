from pathlib import Path

import pytest

from .. import template, template_settings


@pytest.mark.parametrize(
    "case", (Path(__file__).parent / "test_dot").glob("*.tmpl"), ids=lambda x: x.name
)
def test_template(snapshot, case: Path):
    template_settings["strip"] = False

    with case.open("r", encoding="utf-8") as ifile:
        _template = ifile.read()
        assert snapshot == template(_template, template_settings)
