# from awesoon.model import Base
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

username = os.environ["DB_USERNAME"]
password = os.environ["DB_PASSWORD"]
dbname = os.environ["DB_NAME"]
host = os.environ["DB_HOST"]
port = os.environ.get("DB_PORT", "5432")
url = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"


engine = create_engine(url, echo=False, future=True)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

