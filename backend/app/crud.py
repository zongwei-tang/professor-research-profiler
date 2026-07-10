import json
from datetime import datetime

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Analysis, ProfessorPaperCache, User


def get_or_create_user(username: str, db: Session = Depends(get_db)) -> User:
    user = db.execute(select(User).where(User.username == username)).scalar()
    if user is None:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_professor_papers_cache(author_id: int, db: Session = Depends(get_db)) -> tuple[list, str] | None:
    cache = db.get(ProfessorPaperCache, author_id)
    if cache is None:
        return None
    return json.loads(cache.papers_json), cache.time # type: ignore


def upsert_professor_papers(
    author_id: int, name: str, papers: list, db: Session = Depends(get_db)
) -> ProfessorPaperCache:
    cache = db.get(ProfessorPaperCache, author_id)
    if cache is None:
        cache = ProfessorPaperCache(author_id=author_id, name=name, papers_json=json.dumps(papers))
        db.add(cache)
    else:
        cache.name = name
        cache.papers_json = json.dumps(papers)
    cache.time = datetime.now().isoformat()
    db.commit()
    db.refresh(cache)
    return cache


def get_one_analysis(
    user_id: int,
    author_id: int,
    interest: str,
    language: str,
    provider: str,
    db: Session = Depends(get_db),
) -> Analysis | None:
    return db.execute(
        select(Analysis).where(
            Analysis.user_id == user_id,
            Analysis.author_id == author_id,
            Analysis.interest == interest,
            Analysis.language == language,
            Analysis.provider == provider,
        )
    ).scalar()


def save_analysis(
    user_id: int,
    author_id: int,
    author_name: str,
    analysis_text: str,
    interest: str,
    language: str,
    provider: str,
    db: Session = Depends(get_db),
) -> Analysis:
    analysis = get_one_analysis(user_id, author_id, interest, language, provider, db)
    if analysis is None:
        analysis = Analysis(
            user_id=user_id,
            author_id=author_id,
            author_name=author_name,
            analysis_text=analysis_text,
            interest=interest,
            language=language,
            provider=provider,
        )
        db.add(analysis)
    else:
        analysis.author_name = author_name
        analysis.analysis_text = analysis_text
    analysis.time = datetime.now().isoformat()
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis_history(user_id: int, db: Session = Depends(get_db)) -> list[Analysis]:
    return list(db.execute(select(Analysis).where(Analysis.user_id == user_id)).scalars())

def delete_one_history(user_id: int, analysis_id: int, db: Session):
    history = db.execute(select(Analysis).where(Analysis.analysis_id == analysis_id, Analysis.user_id == user_id)).scalar()
    if history is None:
        return None
    db.delete(history)
    db.commit()
    return history

def delete_history_list(user_id: int, db: Session):
    result = db.execute(delete(Analysis).where(Analysis.user_id == user_id))
    if result.rowcount == 0: # type: ignore
        return None
    db.commit() 
    return result.rowcount # type: ignore