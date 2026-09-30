from sqlalchemy import create_engine, text

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print("Database connection successful!")
        print("Query result:", result.scalar())

except Exception as error:
    print("Database connection failed!")
    print("Error:", error)

finally:
    engine.dispose()