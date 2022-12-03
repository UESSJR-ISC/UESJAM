from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

Database = declarative_base()

engine = create_engine("sqlite:///UESJAM.db")
session = scoped_session(sessionmaker(bind=engine))

def get_db_session():
    return session