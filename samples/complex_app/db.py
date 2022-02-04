from urllib.parse import urlparse

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from .settings import settings

metadata = sqlalchemy.MetaData()

configuration = sqlalchemy.Table(
    "configuration",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("saleor_domain", sqlalchemy.String),
    sqlalchemy.Column("auth_token", sqlalchemy.String),
    sqlalchemy.Column("webhook_id", sqlalchemy.String),
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


def get_domain_config(db, saleor_domain: str):
    if saleor_domain.startswith("http"):
        saleor_domain = urlparse(saleor_domain).netloc

    return (
        db.query(configuration)
        .filter(
            configuration.c.saleor_domain == saleor_domain,
        )
        .first()
    )


def update_domain_config(
    db, saleor_domain: str, auth_token: str, webhook_id: str, webhook_secret: str
):
    db_config = get_domain_config(db, saleor_domain)
    stmt = (
        configuration.update()
        .where(configuration.c.id == db_config.id)
        .values(
            auth_token=auth_token,
            webhook_id=webhook_id,
            webhook_secret=webhook_secret,
        )
    )
    db.execute(stmt)
    db.commit()
