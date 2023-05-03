from pathlib import Path

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from .. import template, template_settings


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


@pytest.mark.parametrize(
    "case", (Path(__file__).parent / "test_dot").glob("*.tmpl"), ids=lambda x: x.name
)
def test_template(snapshot_json, case: Path):
    setting = template_settings._replace(strip=False)

    with case.open("r", encoding="utf-8") as ifile:
        _template = ifile.read()
        assert snapshot_json == template(_template, setting)
