from app.models.customer import Customer
from app.models.product import Product


def test_list_reviews_empty(client):
    response = client.get("/api/v1/reviews")
    assert response.status_code == 200
    assert response.json() == []


def test_create_review_success(client, db_session):
    customer = Customer(name="Reviewer Customer", email="reviewer@example.com")
    product = Product(name="Reviewed Product", price=40.0, stock_quantity=10)
    db_session.add(customer)
    db_session.add(product)
    db_session.commit()

    response = client.post(
        "/api/v1/reviews",
        json={
            "customer_id": customer.id,
            "product_id": product.id,
            "rating": 5,
            "comment": "Excellent quality!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer.id
    assert data["product_id"] == product.id
    assert data["rating"] == 5
    assert data["comment"] == "Excellent quality!"


def test_create_review_invalid_rating(client, db_session):
    customer = Customer(name="Invalid Rating Customer", email="invalid.rating@example.com")
    product = Product(name="Invalid Rating Product", price=20.0, stock_quantity=5)
    db_session.add(customer)
    db_session.add(product)
    db_session.commit()

    # Rating above 5
    response = client.post(
        "/api/v1/reviews",
        json={
            "customer_id": customer.id,
            "product_id": product.id,
            "rating": 10,
            "comment": "Invalid rating test",
        },
    )
    assert response.status_code == 422


def test_get_review_by_id(client, db_session):
    customer = Customer(name="Get Review Customer", email="get.review@example.com")
    product = Product(name="Get Review Product", price=15.0, stock_quantity=5)
    db_session.add(customer)
    db_session.add(product)
    db_session.commit()

    rev_res = client.post(
        "/api/v1/reviews",
        json={"customer_id": customer.id, "product_id": product.id, "rating": 4, "comment": "Good"},
    )
    review_id = rev_res.json()["id"]

    response = client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200
    assert response.json()["id"] == review_id


def test_update_review(client, db_session):
    customer = Customer(name="Update Review Customer", email="update.review@example.com")
    product = Product(name="Update Review Product", price=30.0, stock_quantity=5)
    db_session.add(customer)
    db_session.add(product)
    db_session.commit()

    rev_res = client.post(
        "/api/v1/reviews",
        json={"customer_id": customer.id, "product_id": product.id, "rating": 3, "comment": "Okay"},
    )
    review_id = rev_res.json()["id"]

    response = client.put(f"/api/v1/reviews/{review_id}", json={"rating": 5, "comment": "Updated to 5 stars!"})
    assert response.status_code == 200
    assert response.json()["rating"] == 5
    assert response.json()["comment"] == "Updated to 5 stars!"


def test_delete_review(client, db_session):
    customer = Customer(name="Delete Review Customer", email="delete.review@example.com")
    product = Product(name="Delete Review Product", price=50.0, stock_quantity=5)
    db_session.add(customer)
    db_session.add(product)
    db_session.commit()

    rev_res = client.post(
        "/api/v1/reviews",
        json={"customer_id": customer.id, "product_id": product.id, "rating": 2, "comment": "Bad"},
    )
    review_id = rev_res.json()["id"]

    delete_res = client.delete(f"/api/v1/reviews/{review_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/api/v1/reviews/{review_id}")
    assert get_res.status_code == 404
