import json
from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis import redis_client as r
from app.models import Analysis, ProfessorPaperCache, User

PAPERS_CACHE_TTL = 60 * 60 * 12
PAPERS_DB_STALE_AFTER = timedelta(days=1)
HISTORY_CACHE_TTL = 60 * 30


def get_user_by_username(username: str, db: Session = Depends(get_db)) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar()


def create_user(username: str, password_hash: str, db: Session = Depends(get_db)) -> User:
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_professor_papers_cache(author_id: int, db: Session = Depends(get_db)) -> tuple[list, str] | None:
    cached_key = f'professor {author_id}'
    cached = r.get(cached_key)
    if cached is not None:
        payload = json.loads(cached) # type: ignore
        return json.loads(payload['papers_json']), payload['time']

    cached = db.get(ProfessorPaperCache, author_id)
    if cached is None:
        return None
    if datetime.now() - cached.update_time > PAPERS_DB_STALE_AFTER: # type: ignore
        return None
    r.setex(cached_key, PAPERS_CACHE_TTL, json.dumps({'papers_json': cached.papers_json, 'time': cached.time}))
    return json.loads(cached.papers_json), cached.time


def upsert_professor_papers(
    author_id: int, name: str, papers: list, db: Session = Depends(get_db)
) -> ProfessorPaperCache:
    cached_key = f'professor {author_id}'
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
    r.setex(cached_key, PAPERS_CACHE_TTL, json.dumps({'papers_json': cache.papers_json, 'time': cache.time}))
    return cache


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
    analysis = Analysis(
        user_id=user_id,
        author_id=author_id,
        author_name=author_name,
        analysis_text=analysis_text,
        interest=interest,
        language=language,
        provider=provider,
        time=datetime.now().isoformat(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    r.delete(f'history {user_id}')
    return analysis


def get_analysis_history(user_id: int, db: Session = Depends(get_db)) -> list[Analysis]:
    cached_key = f'history {user_id}'
    cached = r.get(cached_key)
    if cached is not None:
        return json.loads(cached)
    else:
        result = list(db.execute(select(Analysis).where(Analysis.user_id == user_id)).scalars())
        serialized = [{
            'analysis_id': i.analysis_id,
            'user_id': i.user_id,
            'author_id': i.author_id,
            'author_name': i.author_name,
            'analysis_text': i.analysis_text,
            'time': i.time,
            'interest': i.interest,
            'language': i.language,
            'provider': i.provider,
        } for i in result]
        r.setex(cached_key, HISTORY_CACHE_TTL, json.dumps(serialized))
        return result

def delete_one_history(user_id: int, analysis_id: int, db: Session):
    history = db.execute(select(Analysis).where(Analysis.analysis_id == analysis_id, Analysis.user_id == user_id)).scalar()
    if history is None:
        return None
    db.delete(history)
    db.commit()
    r.delete(f'history {user_id}')
    return history

def delete_history_list(user_id: int, db: Session):
    result = db.execute(delete(Analysis).where(Analysis.user_id == user_id))
    if result.rowcount == 0: # type: ignore
        return None
    db.commit() 
    r.delete(f'history {user_id}')
    return result.rowcount # type: ignore