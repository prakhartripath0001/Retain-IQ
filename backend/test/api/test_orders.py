from app.models.customer import Customer
from app.models.product import Product


def test_list_orders_empty(client):
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_create_order_success(client, db_session):
    customer = Customer(name="Order Customer", email="order.customer@example.com")
    product = Product(name="Order Product", price=50.0, stock_quantity=100)
    db_session.add(customer)
    db_session.add(product)
    db_session.commit()

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.id,
            "status": "completed",
            "total_amount": 100.0,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 2,
                    "unit_price": 50.0,
                }
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer.id
    assert data["status"] == "completed"
    assert data["total_amount"] == 100.0
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product.id


def test_create_order_customer_not_found(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": 999999,
            "status": "pending",
            "total_amount": 50.0,
            "items": [],
        },
    )
    assert response.status_code == 404


def test_get_order_by_id(client, db_session):
    customer = Customer(name="Get Order Customer", email="get.order@example.com")
    db_session.add(customer)
    db_session.commit()

    create_res = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.id,
            "status": "pending",
            "total_amount": 150.0,
            "items": [],
        },
    )
    order_id = create_res.json()["id"]

    response = client.get(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id
    assert response.json()["total_amount"] == 150.0


def test_get_missing_order(client):
    response = client.get("/api/v1/orders/999999")
    assert response.status_code == 404


def test_update_order(client, db_session):
    customer = Customer(name="Update Order Customer", email="update.order@example.com")
    db_session.add(customer)
    db_session.commit()

    create_res = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.id,
            "status": "pending",
            "total_amount": 200.0,
            "items": [],
        },
    )
    order_id = create_res.json()["id"]

    response = client.put(
        f"/api/v1/orders/{order_id}",
        json={"status": "shipped", "total_amount": 220.0},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"
    assert response.json()["total_amount"] == 220.0


def test_delete_order(client, db_session):
    customer = Customer(name="Delete Order Customer", email="delete.order@example.com")
    db_session.add(customer)
    db_session.commit()

    create_res = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.id,
            "status": "pending",
            "total_amount": 75.0,
            "items": [],
        },
    )
    order_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/orders/{order_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/api/v1/orders/{order_id}")
    assert get_res.status_code == 404
