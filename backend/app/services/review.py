from sqlalchemy.orm import Session

from app.repositories.customer import CustomerRepository
from app.repositories.product import ProductRepository
from app.repositories.review import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewNotFoundError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class ReviewService:
    def __init__(self):
        self.repository = ReviewRepository()
        self.product_repository = ProductRepository()
        self.customer_repository = CustomerRepository()

    def get_review(self, db: Session, review_id: int):
        review = self.repository.get_by_id(db, review_id)
        if review is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        return review

    def list_reviews(
        self,
        db: Session,
        product_id: int | None = None,
        customer_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ):
        return self.repository.list_reviews(
            db, product_id=product_id, customer_id=customer_id, skip=skip, limit=limit
        )

    def create_review(self, db: Session, data: ReviewCreate):
        product = self.product_repository.get_by_id(db, data.product_id)
        if product is None:
            raise ResourceNotFoundError(f"Product {data.product_id} was not found")

        customer = self.customer_repository.get_by_id(db, data.customer_id)
        if customer is None:
            raise ResourceNotFoundError(f"Customer {data.customer_id} was not found")

        return self.repository.create(db, data)

    def update_review(self, db: Session, review_id: int, data: ReviewUpdate):
        review = self.get_review(db, review_id)
        return self.repository.update(db, review, data)

    def delete_review(self, db: Session, review_id: int):
        review = self.get_review(db, review_id)
        self.repository.delete(db, review)
