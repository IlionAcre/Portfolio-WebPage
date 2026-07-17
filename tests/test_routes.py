def test_home_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_projects_route_serves_same_page_as_home(client):
    resp = client.get("/projects")
    assert resp.status_code == 200
    assert b"Test Project" in resp.data


def test_home_renders_fake_project_and_skill(client):
    resp = client.get("/")
    html = resp.get_data(as_text=True)
    assert "Test Project" in html
    assert "Python" in html


def test_robots_txt(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert b"Disallow: /admin/" in resp.data


def test_sitemap_xml(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert b"<urlset" in resp.data


def test_unknown_route_is_404(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404
