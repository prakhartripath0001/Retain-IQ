# Database Schema Design

This document provides the Entity-Relationship (ER) diagram for the E-Commerce database designed for the Retain-IQ platform.

## ER Diagram

```mermaid
erDiagram
    app_users {
        int id PK
        string name
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }

    revoked_tokens {
        string jti PK
        datetime expires_at
    }

    customers {
        int id PK
        string name
        string email UK
        string phone
        datetime created_at
    }

    products {
        int id PK
        string name
        text description
        decimal price
        int stock_quantity
        datetime created_at
    }

    orders {
        int id PK
        int customer_id FK
        string status
        decimal total_amount
        datetime created_at
    }

    order_items {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }

    payments {
        int id PK
        int order_id FK "UK"
        decimal amount
        string payment_method
        string status
        string transaction_id
        datetime created_at
    }

    reviews {
        int id PK
        int product_id FK
        int customer_id FK
        int rating
        text comment
        datetime created_at
    }

    customers ||--o{ orders : places
    customers ||--o{ reviews : writes
    products ||--o{ order_items : contains
    products ||--o{ reviews : receives
    orders ||--|{ order_items : includes
    orders ||--o| payments : has
```

### Table Relationships

*   **Customer ↔ Order:** One-to-Many (`customers` place multiple `orders`).
*   **Order ↔ OrderItem:** One-to-Many (`orders` contain multiple `order_items`).
*   **Product ↔ OrderItem:** One-to-Many (`products` are part of multiple `order_items`).
*   **Order ↔ Payment:** One-to-One (Each `order` has one specific `payment` record).
*   **Customer ↔ Review:** One-to-Many (`customers` write multiple `reviews`).
*   **Product ↔ Review:** One-to-Many (`products` have multiple `reviews`).
*   **User:** Independent table for platform administrative users.
