def test_security_headers_present(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert resp.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


def test_csp_locks_script_src_to_self_only(client):
    resp = client.get("/")
    csp = resp.headers["Content-Security-Policy"]
    assert "script-src 'self'" in csp
    assert "unsafe-inline" not in csp


def test_csp_allows_google_fonts_but_nothing_else_for_style(client):
    resp = client.get("/")
    csp = resp.headers["Content-Security-Policy"]
    assert "style-src 'self' https://fonts.googleapis.com" in csp
