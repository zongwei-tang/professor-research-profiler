from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, insert_default=func.now(), default=datetime.now, comment="创建时间")
    update_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, insert_default=func.now(), onupdate=func.now(), default=datetime.now, comment="修改时间")

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[Optional[str]]


class ProfessorPaperCache(Base):
    __tablename__ = "professor_papers"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    papers_json: Mapped[str]
    time: Mapped[Optional[str]]


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        UniqueConstraint("user_id", "author_id", "interest", "language", "provider"),
    )

    analysis_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    author_id: Mapped[int]
    author_name: Mapped[str]
    analysis_text: Mapped[str]
    time: Mapped[Optional[str]]
    interest: Mapped[str]
    language: Mapped[str]
    provider: Mapped[str]
