def test_refresh_without_token_is_rejected(client):
    resp = client.post("/admin/refresh")
    assert resp.status_code == 403


def test_refresh_with_wrong_token_is_rejected(client):
    resp = client.post("/admin/refresh", headers={"X-Refresh-Token": "wrong-token"})
    assert resp.status_code == 403


def test_refresh_with_correct_token_succeeds(client):
    resp = client.post("/admin/refresh", headers={"X-Refresh-Token": "test-refresh-token"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_refresh_under_dev_server_does_not_report_all_workers_reloading(client):
    """The Flask test client doesn't set SERVER_SOFTWARE to a gunicorn-style
    value, so this should behave like local dev: no signal attempted."""
    resp = client.post("/admin/refresh", headers={"X-Refresh-Token": "test-refresh-token"})
    assert resp.get_json()["all_workers_reloading"] is False


def test_refresh_is_exempt_from_csrf(client):
    """No csrf_token needed - it's meant to be called via curl/webhook,
    authenticated by the token instead."""
    resp = client.post("/admin/refresh", headers={"X-Refresh-Token": "test-refresh-token"})
    assert resp.status_code != 400


def test_refresh_failure_returns_500(client):
    import data
    original = data.load_content
    data.load_content = lambda: (_ for _ in ()).throw(RuntimeError("S3 is down"))
    try:
        resp = client.post("/admin/refresh", headers={"X-Refresh-Token": "test-refresh-token"})
        assert resp.status_code == 500
    finally:
        data.load_content = original
