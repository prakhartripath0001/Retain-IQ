
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


class CustomerRepository:
    def get_by_id(self, db: Session, customer_id: int):
        return db.get(Customer, customer_id)

    def get_by_email(self, db: Session, email: str):
        statement = select(Customer).where(
            Customer.email == email
        )
        return db.scalar(statement)

    def list_customers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ):
        statement = (
            select(Customer)
            .order_by(Customer.id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    def create(self, db: Session, data: CustomerCreate):
        customer = Customer(
            name=data.name,
            email=str(data.email),
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer