from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse

from app.api import analyze, history, professors, users
from app.core.rate_limit import token_bucket

@asynccontextmanager
async def lifespan(app: FastAPI):
    for tb in token_bucket.values():
        tb.start()
    yield

app = FastAPI(title="Professor Research Profiler", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={'detail': 'Something went wrong. Please try again later.'})

app.include_router(professors.router)
app.include_router(analyze.router)
app.include_router(users.router)
app.include_router(history.router)