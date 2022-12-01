from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Database = declarative_base()

engine = create_engine("sqlite:///UESJAM.db")
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session()