from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewRepository:
    def get_by_id(self, db: Session, review_id: int) -> Review | None:
        return db.get(Review, review_id)

    def list_reviews(
        self,
        db: Session,
        product_id: int | None = None,
        customer_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Review]:
        statement = select(Review)
        if product_id is not None:
            statement = statement.where(Review.product_id == product_id)
        if customer_id is not None:
            statement = statement.where(Review.customer_id == customer_id)
        statement = statement.order_by(Review.id.desc()).offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    def create(self, db: Session, data: ReviewCreate) -> Review:
        review = Review(
            product_id=data.product_id,
            customer_id=data.customer_id,
            rating=data.rating,
            comment=data.comment,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    def update(self, db: Session, review: Review, data: ReviewUpdate) -> Review:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)
        db.commit()
        db.refresh(review)
        return review

    def delete(self, db: Session, review: Review) -> None:
        db.delete(review)
        db.commit()
