import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

load_dotenv()

DB_HOST: str = os.getenv("DB_HOST", "")
DB_PORT: str = os.getenv("DB_PORT", "3306")
DB_USER: str = os.getenv("DB_USER", "")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DB_NAME: str = os.getenv("DB_NAME", "")

if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError(
        "Faltan variables de entorno. Asegúrate de tener: "
        "DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
    )

DB_PASSWORD_ESCAPED: str = quote_plus(DB_PASSWORD)

DATABASE_URL: str = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ESCAPED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()