from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from src.config import settings

database = Database(settings.DATABASE_URL)
metadata = MetaData()

# CallerID Table (Mockable, swappable for Postgres later)
callers = Table(
    "callers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("phone_number", String, unique=True, index=True),
    Column("name", String),
    Column("is_senior", Boolean, default=True),
    Column("safety_score", Integer, default=100),
)

engine = create_engine(
    settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"), 
    connect_args={"check_same_thread": False}
)

def init_db():
    metadata.create_all(engine)
