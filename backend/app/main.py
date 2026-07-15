from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analyze, history, professors, users
from app.core.config import settings
from app.core.rate_limit import token_bucket

@asynccontextmanager
async def lifespan(app: FastAPI):
    for tb in token_bucket.values():
        tb.start()
    yield

app = FastAPI(title="Professor Research Profiler", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={'detail': 'Something went wrong. Please try again later.'})

app.include_router(professors.router)
app.include_router(analyze.router)
app.include_router(users.router)
app.include_router(history.router)