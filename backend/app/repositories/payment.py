from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentRepository:
    def get_by_id(self, db: Session, payment_id: int) -> Payment | None:
        return db.get(Payment, payment_id)

    def get_by_order_id(self, db: Session, order_id: int) -> Payment | None:
        statement = select(Payment).where(Payment.order_id == order_id)
        return db.scalar(statement)

    def list_payments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Payment]:
        statement = (
            select(Payment)
            .order_by(Payment.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    def create(self, db: Session, data: PaymentCreate) -> Payment:
        payment = Payment(
            order_id=data.order_id,
            amount=data.amount,
            payment_method=data.payment_method,
            status=data.status,
            transaction_id=data.transaction_id,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def update(self, db: Session, payment: Payment, data: PaymentUpdate) -> Payment:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        db.commit()
        db.refresh(payment)
        return payment

    def delete(self, db: Session, payment: Payment) -> None:
        db.delete(payment)
        db.commit()
