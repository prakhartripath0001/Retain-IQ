def test_list_products_empty(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product_success(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Wireless Mouse",
            "description": "Ergonomic optical mouse",
            "price": 29.99,
            "stock_quantity": 50,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Wireless Mouse"
    assert data["price"] == 29.99
    assert data["stock_quantity"] == 50


def test_get_product_by_id(client):
    create_res = client.post(
        "/api/v1/products",
        json={
            "name": "Gaming Keyboard",
            "price": 89.99,
            "stock_quantity": 25,
        },
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Gaming Keyboard"


def test_get_missing_product(client):
    response = client.get("/api/v1/products/999999")
    assert response.status_code == 404


def test_update_product(client):
    create_res = client.post(
        "/api/v1/products",
        json={
            "name": "USB Cable",
            "price": 9.99,
            "stock_quantity": 100,
        },
    )
    product_id = create_res.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={"price": 14.99, "stock_quantity": 80},
    )
    assert response.status_code == 200
    assert response.json()["price"] == 14.99
    assert response.json()["stock_quantity"] == 80


def test_delete_product(client):
    create_res = client.post(
        "/api/v1/products",
        json={
            "name": "Delete Target Product",
            "price": 19.99,
            "stock_quantity": 5,
        },
    )
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/products/{product_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/api/v1/products/{product_id}")
    assert get_res.status_code == 404
