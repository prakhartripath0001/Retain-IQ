def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Analyst",
            "email": "test.analyst@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Analyst"
    assert data["email"] == "test.analyst@example.com"
    assert data["role"] == "ANALYST"
    assert data["is_active"] is True


def test_duplicate_registration(client):
    payload = {
        "name": "Test Analyst",
        "email": "duplicate@example.com",
        "password": "Strong-Test-Password-123!",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert second_response.status_code == 409


def test_login_success(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Wrong Password User",
            "email": "wrongpassword@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrongpassword@example.com",
            "password": "Wrong-Password-123!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "doesnotexist@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert response.status_code == 401


def test_me_with_valid_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Me Test User",
            "email": "me@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "me@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "me@example.com"
    assert data["name"] == "Me Test User"
    assert data["role"] == "ANALYST"


def test_me_without_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_logout_revokes_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Logout User",
            "email": "logout@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "logout@example.com",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    me_response = client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert me_response.status_code == 200

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers=headers,
    )

    assert logout_response.status_code == 204

    me_after_logout = client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert me_after_logout.status_code == 401