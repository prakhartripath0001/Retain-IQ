
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerNotFoundError(Exception):
    pass


class DuplicateCustomerError(Exception):
    pass


class CustomerService:
    def __init__(self):
        self.repository = CustomerRepository()

    def get_customer(self, db: Session, customer_id: int):
        customer = self.repository.get_by_id(db, customer_id)

        if customer is None:
            raise CustomerNotFoundError(
                f"Customer {customer_id} was not found"
            )

        return customer

    def list_customers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ):
        return self.repository.list_customers(
            db,
            skip=skip,
            limit=limit,
        )

    def create_customer(self, db: Session, data: CustomerCreate):
        existing = self.repository.get_by_email(
            db,
            str(data.email),
        )

        if existing:
            raise DuplicateCustomerError(
                "A customer with this email already exists"
            )

        try:
            return self.repository.create(db, data)
        except IntegrityError as exc:
            db.rollback()
            raise DuplicateCustomerError(
                "The customer could not be created because "
                "a database constraint was violated"
            ) from exc