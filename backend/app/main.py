from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import analyze, history, professors, users
from app.core.rate_limit import token_bucket

@asynccontextmanager
async def lifespan(app: FastAPI):
    for tb in token_bucket.values():
        tb.start()
    yield

app = FastAPI(title="Professor Research Profiler", lifespan=lifespan)

app.include_router(professors.router)
app.include_router(analyze.router)
app.include_router(users.router)
app.include_router(history.router)