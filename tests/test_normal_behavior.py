def test_login_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Secure Banking Portal" in response.data


def test_valid_login_opens_dashboard(client):
    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "alice-demo-123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Alice Johnson" in response.data
    assert b"DEMO-1001" in response.data


def test_invalid_login_is_rejected(client):
    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "incorrect-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get(
        "/dashboard",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_logout_ends_session(client):
    client.post(
        "/login",
        data={
            "username": "alice",
            "password": "alice-demo-123",
        },
    )

    client.post("/logout")

    response = client.get(
        "/dashboard",
        follow_redirects=False,
    )

    assert response.status_code == 302