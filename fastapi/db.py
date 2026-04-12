from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os


class Base(DeclarativeBase):
    pass


def get_engine():
    load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    port = os.getenv("PORT")
    db_name = os.getenv("DB_NAME")
    host = os.getenv("HOST")

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    if not database_exists(db_url):
        create_database(db_url)
    return create_engine(db_url)


engine = get_engine()
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
