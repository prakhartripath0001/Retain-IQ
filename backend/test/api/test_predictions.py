from app.models.customer import Customer


def test_predict_churn_success(client, db_session):
    customer = Customer(name="Prediction Customer", email="prediction.test@example.com")
    db_session.add(customer)
    db_session.commit()

    response = client.post(f"/api/v1/predictions/churn/{customer.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == customer.id
    assert 0.0 <= data["probability"] <= 1.0
    assert data["risk_level"] in ["HIGH", "MEDIUM", "LOW"]
    assert isinstance(data["factors"], list)


def test_predict_churn_missing_customer(client):
    response = client.post("/api/v1/predictions/churn/999999")
    assert response.status_code == 404
