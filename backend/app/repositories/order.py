from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate


class OrderRepository:
    def get_by_id(self, db: Session, order_id: int) -> Order | None:
        return db.get(Order, order_id)

    def list_orders(
        self,
        db: Session,
        customer_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Order]:
        statement = select(Order)
        if customer_id is not None:
            statement = statement.where(Order.customer_id == customer_id)
        statement = statement.order_by(Order.id.desc()).offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    def create(self, db: Session, data: OrderCreate) -> Order:
        order = Order(
            customer_id=data.customer_id,
            status=data.status,
            total_amount=data.total_amount,
        )
        db.add(order)
        db.flush()

        for item_data in data.items:
            item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
            )
            db.add(item)

        db.commit()
        db.refresh(order)
        return order

    def update(self, db: Session, order: Order, data: OrderUpdate) -> Order:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        db.commit()
        db.refresh(order)
        return order

    def delete(self, db: Session, order: Order) -> None:
        db.delete(order)
        db.commit()
