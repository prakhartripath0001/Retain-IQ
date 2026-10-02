from app.models.customer import Customer
from app.models.order import Order


def test_get_analytics_overview(client, db_session):
    customer = Customer(name="Analytics Customer", email="analytics.overview@example.com")
    db_session.add(customer)
    db_session.commit()

    order = Order(customer_id=customer.id, status="completed", total_amount=250.0)
    db_session.add(order)
    db_session.commit()

    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "customers" in data
    assert "orders" in data
    assert "churn_rate" in data
    assert "average_order_value" in data
    assert data["total_revenue"] >= 250.0
    assert data["customers"] >= 1
    assert data["orders"] >= 1


def test_get_analytics_revenue(client, db_session):
    customer = Customer(name="Revenue Customer", email="analytics.revenue@example.com")
    db_session.add(customer)
    db_session.commit()

    order = Order(customer_id=customer.id, status="completed", total_amount=150.0)
    db_session.add(order)
    db_session.commit()

    response = client.get("/api/v1/analytics/revenue")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "average_order_value" in data
    assert "monthly_revenue" in data
    assert isinstance(data["monthly_revenue"], list)


def test_get_analytics_customers(client, db_session):
    customer = Customer(name="Customer Analytics", email="analytics.customer@example.com")
    db_session.add(customer)
    db_session.commit()

    order = Order(customer_id=customer.id, status="completed", total_amount=300.0)
    db_session.add(order)
    db_session.commit()

    response = client.get("/api/v1/analytics/customers")
    assert response.status_code == 200
    data = response.json()
    assert "total_customers" in data
    assert "buying_customers" in data
    assert "avg_orders_per_customer" in data
    assert "avg_customer_spend" in data
    assert data["total_customers"] >= 1
    assert data["buying_customers"] >= 1


def test_get_analytics_segments(client):
    response = client.get("/api/v1/analytics/segments")
    assert response.status_code == 200
    data = response.json()
    assert "total_segments" in data
    assert "segments" in data
    assert isinstance(data["segments"], list)


def test_get_analytics_churn(client):
    response = client.get("/api/v1/analytics/churn")
    assert response.status_code == 200
    data = response.json()
    assert "total_eligible_customers" in data
    assert "churned_customers" in data
    assert "retained_customers" in data
    assert "churn_rate" in data
