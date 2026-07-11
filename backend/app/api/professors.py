import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.redis import redis_client as r
from app.schemas import PaperCacheResponse, PaperFetchRequest, ProfessorCandidate
from app.services import semantic_scholar

router = APIRouter(prefix="/api/professors", tags=["professors"])


@router.get("/search", response_model=list[ProfessorCandidate])
def search_professors(name: str):
    cached_key = f'professor {name}'
    candidates = r.get(cached_key)
    if candidates:
        return json.loads(candidates) # type: ignore
    else:
        candidates = semantic_scholar.search_author(name)
        if candidates is None:
            raise HTTPException(status_code=502, detail="Failed to search Semantic Scholar")
        r.setex(cached_key, 60 * 60 * 72, json.dumps(candidates))
        return candidates


@router.post("/papers/fetch", response_model=PaperCacheResponse)
def fetch_professor_papers(request: PaperFetchRequest, db: Session = Depends(get_db)):
    papers = semantic_scholar.get_papers(str(request.author_id))
    if papers is None:
        raise HTTPException(status_code=502, detail="Failed to fetch papers from Semantic Scholar")
    if not papers:
        raise HTTPException(status_code=404, detail="No papers with abstracts found for this professor")
    cache = crud.upsert_professor_papers(request.author_id, request.author_name, papers, db)
    return PaperCacheResponse(papers=json.loads(cache.papers_json), time=cache.time)


@router.get("/{author_id}/papers", response_model=PaperCacheResponse)
def get_professor_papers_cache(author_id: int, db: Session = Depends(get_db)):
    result = crud.get_professor_papers_cache(author_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="No cached papers for this professor")
    papers, time = result
    return PaperCacheResponse(papers=papers, time=time)