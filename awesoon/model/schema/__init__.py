import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
from awesoon.model.schema import scan, shop, doc

username = os.environ["DB_USERNAME"]
password = os.environ["DB_PASSWORD"]
dbname = os.environ["DB_NAME"]
host = os.environ["DB_HOST"]
port = os.environ.get("DB_PORT", "5432")
url = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"

engine = create_engine(url, echo=False, future=True)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
