from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas import AnalyzeRequest
import app.crud as crud
import app.services.llm_router as llm_router
import app.services.semantic_scholar as semantic_scholar
from app.core.analysis_job import job_list
from app.core.database import get_db


async def analyze(request: AnalyzeRequest, user_id: int, job_id: str):
    db: Session = next(get_db())
    try:
        job_list[job_id].status = "fetching papers"
        cached = crud.get_professor_papers_cache(request.author_id, db)
        if cached is not None:
            papers, _ = cached
        else:
            papers = await semantic_scholar.get_papers(str(request.author_id))
            if not papers:
                job_list[job_id].status = "failed"
                raise HTTPException(status_code=404, detail="No papers with abstracts found for this professor")
            crud.upsert_professor_papers(request.author_id, request.author_name, papers, db)

        job_list[job_id].status = "llm processing"

        top5, by_year, coauthor = semantic_scholar.compute(papers)
        author = {"authorId": request.author_id, "name": request.author_name}
        prompt_text = llm_router.prompt(author, top5, by_year, coauthor, request.interest, request.language)
        analysis_text, provider = await llm_router.llm_process(request.provider, prompt_text) # type: ignore
        if analysis_text is None:
            job_list[job_id].status = "failed"
            raise HTTPException(status_code=502, detail="Failed to get analysis from the LLM provider")

        result = crud.save_analysis(
            user_id,
            request.author_id,
            request.author_name,
            analysis_text,
            request.interest,
            request.language,
            provider,
            db,
        )

        result.provider_change = provider != request.provider # type: ignore [AnalysisResponse have provider_change attribute]
        result.status = "completed" # type: ignore
        result.job_id = job_id # type: ignore
        result.papers = papers # type: ignore

        job_list[job_id] = result
    except Exception:
        if job_list[job_id].status != "failed": # type: ignore
            job_list[job_id].status = "failed" # type: ignore
        raise
    finally:
        db.close()