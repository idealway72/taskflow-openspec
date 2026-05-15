import os
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Strip channel_binding — not supported by psycopg2
    parsed = urlparse(DATABASE_URL)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("channel_binding", None)
    new_query = urlencode({k: v[0] for k, v in params.items()})
    DATABASE_URL = urlunparse(parsed._replace(query=new_query))
    connect_args = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
