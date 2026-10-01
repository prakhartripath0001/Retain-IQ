from sqlalchemy.orm import Session

from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate


class OrderNotFoundError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class OrderService:
    def __init__(self):
        self.repository = OrderRepository()
        self.customer_repository = CustomerRepository()

    def get_order(self, db: Session, order_id: int):
        order = self.repository.get_by_id(db, order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} was not found")
        return order

    def list_orders(
        self,
        db: Session,
        customer_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ):
        return self.repository.list_orders(
            db, customer_id=customer_id, skip=skip, limit=limit
        )

    def create_order(self, db: Session, data: OrderCreate):
        customer = self.customer_repository.get_by_id(db, data.customer_id)
        if customer is None:
            raise CustomerNotFoundError(
                f"Customer {data.customer_id} was not found"
            )
        return self.repository.create(db, data)

    def update_order(self, db: Session, order_id: int, data: OrderUpdate):
        order = self.get_order(db, order_id)
        return self.repository.update(db, order, data)

    def delete_order(self, db: Session, order_id: int):
        order = self.get_order(db, order_id)
        self.repository.delete(db, order)
