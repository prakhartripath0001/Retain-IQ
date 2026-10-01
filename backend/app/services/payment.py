from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentNotFoundError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass


class DuplicatePaymentError(Exception):
    pass


class PaymentService:
    def __init__(self):
        self.repository = PaymentRepository()
        self.order_repository = OrderRepository()

    def get_payment(self, db: Session, payment_id: int):
        payment = self.repository.get_by_id(db, payment_id)
        if payment is None:
            raise PaymentNotFoundError(f"Payment {payment_id} was not found")
        return payment

    def list_payments(self, db: Session, skip: int = 0, limit: int = 50):
        return self.repository.list_payments(db, skip=skip, limit=limit)

    def create_payment(self, db: Session, data: PaymentCreate):
        order = self.order_repository.get_by_id(db, data.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {data.order_id} was not found")

        existing = self.repository.get_by_order_id(db, data.order_id)
        if existing:
            raise DuplicatePaymentError(
                f"A payment for order {data.order_id} already exists"
            )

        try:
            return self.repository.create(db, data)
        except IntegrityError as exc:
            db.rollback()
            raise DuplicatePaymentError(
                "Payment could not be created due to database constraints"
            ) from exc

    def update_payment(self, db: Session, payment_id: int, data: PaymentUpdate):
        payment = self.get_payment(db, payment_id)
        return self.repository.update(db, payment, data)

    def delete_payment(self, db: Session, payment_id: int):
        payment = self.get_payment(db, payment_id)
        self.repository.delete(db, payment)
