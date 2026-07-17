import base64
import os
import sys

import pytest

from conftest import REQUIRED_ENV, make_fake_s3_client

SAMPLE_SVG = '<svg><path d="M0 0 L1 1"/></svg>'


@pytest.fixture
def data_module(monkeypatch, tmp_path):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    images = [
        {"Key": "images/icon-Github.svg", "Body": SAMPLE_SVG.encode()},
        {"Key": "images/skill-Python.svg", "Body": SAMPLE_SVG.encode()},
        {"Key": "images/project_2.gif", "Body": b"fake-gif-bytes"},
    ]
    monkeypatch.setattr("boto3.client", lambda *a, **kw: make_fake_s3_client(images))

    sys.modules.pop("data", None)
    import data as data_module

    # Redirect both dirs into a throwaway tmp_path so this test never
    # touches the real static/ folder.
    monkeypatch.setattr(data_module, "PROJECT_GIFS_DIR", str(tmp_path / "generated"))
    monkeypatch.setattr(data_module, "OPTIMIZED_PROJECTS_DIR", str(tmp_path / "optimized"))

    yield data_module

    sys.modules.pop("data", None)


def test_load_content_parses_fake_skills_and_projects(data_module):
    data_module.load_content()
    assert data_module.skill_list == [{"name": "Python", "type": "technical"}]
    assert data_module.project_list[0]["title"] == "Test Project"


def test_social_icon_svg_is_parsed_into_inline_path_data(data_module):
    data_module.load_content()
    assert data_module.icons["social"]["icon-Github"] == ["M0 0 L1 1"]


def test_skill_icon_svg_is_base64_encoded(data_module):
    data_module.load_content()
    encoded = data_module.icons["skill"]["skill-Python"]
    assert encoded.startswith("data:image/svg+xml;base64,")
    raw = base64.b64decode(encoded.split(",", 1)[1]).decode()
    assert raw == SAMPLE_SVG


def test_gif_without_optimized_version_is_fetched_and_written_to_disk(data_module):
    data_module.load_content()
    assert data_module.icons["projects"]["2"] == "generated/projects/2.gif"
    written_path = os.path.join(data_module.PROJECT_GIFS_DIR, "2.gif")
    assert os.path.exists(written_path)
    with open(written_path, "rb") as f:
        assert f.read() == b"fake-gif-bytes"


def test_gif_with_optimized_version_skips_s3_fetch_entirely(data_module):
    os.makedirs(data_module.OPTIMIZED_PROJECTS_DIR, exist_ok=True)
    optimized_path = os.path.join(data_module.OPTIMIZED_PROJECTS_DIR, "2.webp")
    with open(optimized_path, "wb") as f:
        f.write(b"fake-webp-bytes")

    data_module.load_content()

    assert data_module.icons["projects"]["2"] == "optimized_projects/2.webp"
    # and it must NOT have also written the raw gif - that fetch should be skipped
    assert not os.path.exists(os.path.join(data_module.PROJECT_GIFS_DIR, "2.gif"))


def test_load_content_rebuilds_icons_from_scratch(data_module):
    """A second load_content() call must not leave stale entries from
    objects that no longer exist in S3."""
    data_module.load_content()
    assert "icon-Github" in data_module.icons["social"]

    data_module.s3_client.list_objects_v2.side_effect = lambda Bucket, Prefix: {"Contents": []}
    data_module.load_content()
    assert data_module.icons["social"] == {}
