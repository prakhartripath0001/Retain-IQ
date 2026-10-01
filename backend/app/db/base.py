from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from app.models.customer import Customer
from app.models.customer_feature import CustomerFeature
from app.models.customer_segment import CustomerSegment
from app.models.model_version import ModelVersion
from app.models.churn_prediction import ChurnPrediction