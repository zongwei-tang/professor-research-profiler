from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud as crud
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas import AnalysisResponse, AnalyzeRequest
from app.services import llm_router, semantic_scholar

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    existing = crud.get_one_analysis(
        user_id, request.author_id, request.interest, request.language, request.provider, db
    )
    if existing is not None:
        return existing

    cached = crud.get_professor_papers_cache(request.author_id, db)
    if cached is not None:
        papers, _ = cached
    else:
        papers = semantic_scholar.get_papers(str(request.author_id))
        if not papers:
            raise HTTPException(status_code=404, detail="No papers with abstracts found for this professor")
        crud.upsert_professor_papers(request.author_id, request.author_name, papers, db)

    top5, by_year, coauthor = semantic_scholar.compute(papers)
    author = {"authorId": request.author_id, "name": request.author_name}
    prompt_text = llm_router.prompt(author, top5, by_year, coauthor, request.interest, request.language)
    analysis_text = llm_router.llm_process(request.provider, prompt_text)
    if analysis_text is None:
        raise HTTPException(status_code=502, detail="Failed to get analysis from the LLM provider")

    return crud.save_analysis(
        user_id,
        request.author_id,
        request.author_name,
        analysis_text,
        request.interest,
        request.language,
        request.provider,
        db,
    )
