from sqlalchemy import create_engine, text
from config import POSTGRES_URL

# Create a SQLAlchemy engine for PostgreSQL
postgres_engine = create_engine(POSTGRES_URL)

def ping_postgres():
    """
    Ping the PostgreSQL database to verify the connection.
    """
    try:
        with postgres_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Postgres connection successful")
    except Exception as e:
        print(f"Postgres connection failed: {e}")