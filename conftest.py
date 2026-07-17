"""Shared pytest fixtures.

main.py and data.py do real work at import time (fail-fast env var checks,
and data.py makes a real boto3 S3 call to load site content) rather than
using an application-factory pattern. To test them without real AWS
credentials or network access, the `app` fixture below sets fake required
env vars and patches boto3.client *before* importing either module, and
force-reimports both on every test so no state (rate-limit counters, mocked
S3 content) leaks between tests.
"""
import base64
import json
import sys
from unittest.mock import MagicMock

import pytest

FAKE_SKILLS = [{"name": "Python", "type": "technical"}]
FAKE_PROJECTS = [
    {
        "id": 1,
        "title": "Test Project",
        "description": "A fake project used only in tests.",
        "links": {"github": "https://example.com/repo"},
    }
]

REQUIRED_ENV = {
    "KEY_ID": "test-key-id",
    "ACCESS_KEY": "test-access-key",
    "REGION": "us-east-1",
    "BUCKET": "test-bucket",
    "FLASK_KEY": "test-flask-secret-key",
    "MAIL_SERVER": "smtp.example.com",
    "MAIL_USERNAME": "test-mail-user",
    "MAIL_PASSWORD": "test-mail-password",
    "MAIL_DEFAULT_SENDER": "test@example.com",
    "REFRESH_TOKEN": "test-refresh-token",
}


def make_fake_s3_client(extra_image_objects=None):
    """A MagicMock standing in for boto3's S3 client, serving fake
    skills/projects JSON and whatever image objects a test needs."""
    client = MagicMock()
    image_objects = extra_image_objects or []

    def get_object(Bucket, Key):
        if Key == "data/skills.json":
            body = json.dumps(FAKE_SKILLS).encode()
        elif Key == "data/projects.json":
            body = json.dumps(FAKE_PROJECTS).encode()
        else:
            match = next((o for o in image_objects if o["Key"] == Key), None)
            body = match["Body"] if match else b""
        return {"Body": MagicMock(read=MagicMock(return_value=body))}

    def list_objects_v2(Bucket, Prefix):
        return {"Contents": [{"Key": o["Key"]} for o in image_objects]}

    client.get_object.side_effect = get_object
    client.list_objects_v2.side_effect = list_objects_v2
    return client


@pytest.fixture
def app(monkeypatch):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr("boto3.client", lambda *a, **kw: make_fake_s3_client())

    # Force a fresh import so each test gets its own Limiter (no leftover
    # rate-limit counts) and re-runs data.load_content() against the mock.
    sys.modules.pop("main", None)
    sys.modules.pop("data", None)

    import main as main_module

    main_module.app.config["TESTING"] = True
    main_module.mail.send = MagicMock()  # never actually send email in tests

    yield main_module.app

    sys.modules.pop("main", None)
    sys.modules.pop("data", None)


@pytest.fixture
def client(app):
    return app.test_client()


def get_csrf_token(client):
    """Fetch a real CSRF token the way a browser would, by loading the page
    first - the client's cookie jar carries the session to the next request."""
    resp = client.get("/")
    html = resp.get_data(as_text=True)
    marker = 'name="csrf_token" value="'
    start = html.index(marker) + len(marker)
    end = html.index('"', start)
    return html[start:end]
