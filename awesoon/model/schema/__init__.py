# from awesoon.model import Base
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain.vectorstores.pgvector import PGVector
from langchain.vectorstores.pgvector import Base
from awesoon.model.schema import shop


username = os.environ["DB_USERNAME"]
password = os.environ["DB_PASSWORD"]
dbname = os.environ["DB_NAME"]
host = os.environ["DB_HOST"]
port = os.environ.get("DB_PORT", "5432")
url = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"


engine = create_engine(url, echo=False, future=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
# pg_base.metadata.create_all(engine)

CONNECTION_STRING_PG_VECTOR = PGVector.connection_string_from_db_params(
    driver="psycopg2",
    host=host,
    port=port,
    database=dbname,
    user=username,
    password=password
)
