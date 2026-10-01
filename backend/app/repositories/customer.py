from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:
    def get_by_id(self, db: Session, customer_id: int) -> Customer | None:
        return db.get(Customer, customer_id)

    def get_by_email(self, db: Session, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        return db.scalar(statement)

    def list_customers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Customer]:
        statement = (
            select(Customer)
            .order_by(Customer.id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    def create(self, db: Session, data: CustomerCreate) -> Customer:
        customer = Customer(
            name=data.name,
            email=str(data.email),
            phone=data.phone,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def update(self, db: Session, customer: Customer, data: CustomerUpdate) -> Customer:
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] is not None:
            update_data["email"] = str(update_data["email"])
        for field, value in update_data.items():
            setattr(customer, field, value)
        db.commit()
        db.refresh(customer)
        return customer

    def delete(self, db: Session, customer: Customer) -> None:
        db.delete(customer)
        db.commit()