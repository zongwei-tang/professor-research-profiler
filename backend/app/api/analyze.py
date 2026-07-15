import uuid

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from app.core.security import get_current_user_id
from app.schemas import AnalysisJobResponse, AnalysisResponse, AnalyzeRequest
from app.core.analysis_job import job_list, AnalysisJob
from app.services import run_analysis

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=AnalysisJobResponse)
async def analyze(request: AnalyzeRequest, background_task: BackgroundTasks, user_id: int = Depends(get_current_user_id)):
    job_id = str(uuid.uuid4())
    job_list[job_id] = AnalysisJob(
        job_id=job_id,
        status="initialized",
        user_id=user_id,
        author_id=request.author_id,
        author_name=request.author_name,
        analysis_text="",
        interest=request.interest,
        language=request.language,
        provider=request.provider,
    )

    background_task.add_task(run_analysis.analyze, request, user_id, job_id)

    return AnalysisJobResponse(status='initialized', job_id=job_id)

@router.get("/{job_id}", response_model=AnalysisJobResponse)
async def get_job_status(job_id: str):
    job = job_list.get(job_id)
    if job is None:
        return AnalysisJobResponse(status='Job not found', job_id=job_id)
    return AnalysisJobResponse(status=job.status, job_id=job_id)

@router.get("/{job_id}/result", response_model=AnalysisResponse)
async def get_job_result(job_id: str):
    job = job_list.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == "failed":
        raise HTTPException(status_code=502, detail="Analysis failed")
    if job.status != "completed":
        raise HTTPException(status_code=409, detail="Job is not completed yet")
    return job