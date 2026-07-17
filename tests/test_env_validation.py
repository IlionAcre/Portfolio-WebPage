import sys

import pytest

from conftest import REQUIRED_ENV, make_fake_s3_client


@pytest.mark.parametrize("missing_var", list(REQUIRED_ENV.keys()))
def test_missing_required_env_var_fails_fast(monkeypatch, missing_var):
    """Every var in main.py/data.py's REQUIRED_ENV_VARS must actually be
    required - if one of these silently stopped being checked, the app
    would start in a broken (or, for FLASK_KEY, insecure) state instead of
    refusing to boot."""
    env = dict(REQUIRED_ENV)
    env[missing_var] = ""
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr("boto3.client", lambda *a, **kw: make_fake_s3_client())

    sys.modules.pop("main", None)
    sys.modules.pop("data", None)

    with pytest.raises(RuntimeError, match=missing_var):
        import main  # noqa: F401

    sys.modules.pop("main", None)
    sys.modules.pop("data", None)
