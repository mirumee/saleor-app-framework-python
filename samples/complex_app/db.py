import sqlalchemy
from sqlalchemy.orm import sessionmaker

from settings import settings

metadata = sqlalchemy.MetaData()

configuration = sqlalchemy.Table(
    "configuration",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("domain_name", sqlalchemy.String, unique=True),
    sqlalchemy.Column("webhook_id", sqlalchemy.String),
    sqlalchemy.Column("webhook_token", sqlalchemy.String),
    sqlalchemy.Column("webhook_secret", sqlalchemy.String),
)


engine = sqlalchemy.create_engine(
    settings.database_dsn, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
