from app.models.customer import Customer


def test_list_payments_empty(client):
    response = client.get("/api/v1/payments")
    assert response.status_code == 200
    assert response.json() == []


def test_create_payment_success(client, db_session):
    customer = Customer(name="Payment Customer", email="payment.test@example.com")
    db_session.add(customer)
    db_session.commit()

    order_res = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.id,
            "status": "completed",
            "total_amount": 150.0,
            "items": [],
        },
    )
    order_id = order_res.json()["id"]

    response = client.post(
        "/api/v1/payments",
        json={
            "order_id": order_id,
            "amount": 150.0,
            "payment_method": "credit_card",
            "status": "paid",
            "transaction_id": "TXN_123456",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == order_id
    assert data["amount"] == 150.0
    assert data["payment_method"] == "credit_card"


def test_create_payment_missing_order(client):
    response = client.post(
        "/api/v1/payments",
        json={
            "order_id": 999999,
            "amount": 100.0,
            "payment_method": "paypal",
            "status": "pending",
        },
    )
    assert response.status_code == 404


def test_get_payment_by_id(client, db_session):
    customer = Customer(name="Get Payment Customer", email="get.payment@example.com")
    db_session.add(customer)
    db_session.commit()

    order_res = client.post(
        "/api/v1/orders",
        json={"customer_id": customer.id, "status": "completed", "total_amount": 200.0, "items": []},
    )
    order_id = order_res.json()["id"]

    pay_res = client.post(
        "/api/v1/payments",
        json={
            "order_id": order_id,
            "amount": 200.0,
            "payment_method": "debit_card",
            "status": "paid",
        },
    )
    payment_id = pay_res.json()["id"]

    response = client.get(f"/api/v1/payments/{payment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_update_payment(client, db_session):
    customer = Customer(name="Update Payment Customer", email="update.payment@example.com")
    db_session.add(customer)
    db_session.commit()

    order_res = client.post(
        "/api/v1/orders",
        json={"customer_id": customer.id, "status": "pending", "total_amount": 75.0, "items": []},
    )
    order_id = order_res.json()["id"]

    pay_res = client.post(
        "/api/v1/payments",
        json={"order_id": order_id, "amount": 75.0, "payment_method": "stripe", "status": "pending"},
    )
    payment_id = pay_res.json()["id"]

    response = client.put(f"/api/v1/payments/{payment_id}", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_payment(client, db_session):
    customer = Customer(name="Delete Payment Customer", email="delete.payment@example.com")
    db_session.add(customer)
    db_session.commit()

    order_res = client.post(
        "/api/v1/orders",
        json={"customer_id": customer.id, "status": "pending", "total_amount": 50.0, "items": []},
    )
    order_id = order_res.json()["id"]

    pay_res = client.post(
        "/api/v1/payments",
        json={"order_id": order_id, "amount": 50.0, "payment_method": "cod", "status": "pending"},
    )
    payment_id = pay_res.json()["id"]

    delete_res = client.delete(f"/api/v1/payments/{payment_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/api/v1/payments/{payment_id}")
    assert get_res.status_code == 404
