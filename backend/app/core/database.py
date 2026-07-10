from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.models import Base

from app.core.config import settings

engine = create_engine(
    f"sqlite+libsql://{settings.turso_db_url}?secure=true",
    connect_args={"auth_token": settings.turso_db_token},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()