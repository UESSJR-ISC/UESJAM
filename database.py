from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///UESJAM.db")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=True)
Database = declarative_base()

def get_session():
    return SessionLocal()