from sqlalchemy.orm import Session

from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductNotFoundError(Exception):
    pass


class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    def get_product(self, db: Session, product_id: int):
        product = self.repository.get_by_id(db, product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} was not found")
        return product

    def list_products(self, db: Session, skip: int = 0, limit: int = 50):
        return self.repository.list_products(db, skip=skip, limit=limit)

    def create_product(self, db: Session, data: ProductCreate):
        return self.repository.create(db, data)

    def update_product(self, db: Session, product_id: int, data: ProductUpdate):
        product = self.get_product(db, product_id)
        return self.repository.update(db, product, data)

    def delete_product(self, db: Session, product_id: int):
        product = self.get_product(db, product_id)
        self.repository.delete(db, product)
