def register_and_login(client, email="customer.test@example.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Customer Test User",
            "email": email,
            "password": "Strong-Test-Password-123!",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "Strong-Test-Password-123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_get_customers_without_authentication(client):
    response = client.get("/api/v1/customers")

    assert response.status_code == 401


def test_get_customer_without_authentication(client):
    response = client.get("/api/v1/customers/1")

    assert response.status_code == 401


def test_create_customer_without_authentication(client):
    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Test Customer",
            "email": "testcustomer@example.com",
        },
    )

    assert response.status_code == 401


def test_create_customer_as_analyst_forbidden(client):
    headers = register_and_login(
        client,
        "customer.analyst@example.com",
    )

    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": "Unauthorized Customer",
            "email": "unauthorized.customer@example.com",
        },
    )

    assert response.status_code == 403


def test_create_customer_as_admin(client, db_session):
    headers = register_and_login(
        client,
        "customer.admin@example.com",
    )

    from app.models.user import User

    user = db_session.query(User).filter(
        User.email == "customer.admin@example.com"
    ).first()

    assert user is not None

    user.role = "ADMIN"
    db_session.commit()

    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": "Admin Created Customer",
            "email": "admin.created.customer@example.com",
        },
    )

    assert response.status_code == 201


def test_get_customers_authenticated(client):
    headers = register_and_login(
        client,
        "customers.list@example.com",
    )

    response = client.get(
        "/api/v1/customers",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_missing_customer(client):
    headers = register_and_login(
        client,
        "customers.missing@example.com",
    )

    response = client.get(
        "/api/v1/customers/999999",
        headers=headers,
    )

    assert response.status_code == 404