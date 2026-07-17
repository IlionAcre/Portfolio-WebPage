from conftest import get_csrf_token

VALID_FORM = {
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Hello",
    "emailContent": "This is a test message.",
}


def test_contact_form_allows_five_then_blocks_the_sixth(client):
    token = get_csrf_token(client)
    for _ in range(5):
        resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token})
        assert resp.status_code == 200

    resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token})
    assert resp.status_code == 429


def test_admin_refresh_allows_five_then_blocks_the_sixth(client):
    headers = {"X-Refresh-Token": "test-refresh-token"}
    for _ in range(5):
        resp = client.post("/admin/refresh", headers=headers)
        assert resp.status_code == 200

    resp = client.post("/admin/refresh", headers=headers)
    assert resp.status_code == 429


def test_rate_limit_is_per_test_not_leaked_from_a_previous_test(client):
    """Sanity check on the test harness itself: the `app` fixture re-imports
    main.py fresh for every test, which should give each test its own
    Flask-Limiter storage. If this fails, some other test's request count
    is leaking in and every rate-limit test above is unreliable."""
    resp = client.post("/admin/refresh", headers={"X-Refresh-Token": "test-refresh-token"})
    assert resp.status_code == 200
