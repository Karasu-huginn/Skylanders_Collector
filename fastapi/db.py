from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

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

engine=get_engine()
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
