from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def get_by_id(self, db: Session, product_id: int) -> Product | None:
        return db.get(Product, product_id)

    def list_products(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Product]:
        statement = (
            select(Product)
            .order_by(Product.id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    def create(self, db: Session, data: ProductCreate) -> Product:
        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db: Session, product: Product, data: ProductUpdate) -> Product:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product: Product) -> None:
        db.delete(product)
        db.commit()
