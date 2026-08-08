"""
tests/test_routes.py — Route Integration Tests
================================================
Verifies that public and protected endpoints respond
with the correct status codes and content.
"""


def test_index_page(client):
    """The landing page loads successfully."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"AI Career Connect" in res.data


def test_login_page(client):
    """The login page renders for unauthenticated users."""
    res = client.get("/auth/login")
    assert res.status_code == 200
    assert b"Welcome Back" in res.data


def test_dashboard_requires_login(client):
    """Dashboard redirects unauthenticated users to login."""
    res = client.get("/dashboard/", follow_redirects=False)
    assert res.status_code in (302, 308)


def test_chat_requires_login(client):
    """Career chat redirects unauthenticated users to login."""
    res = client.get("/career/chat", follow_redirects=False)
    assert res.status_code in (302, 308)