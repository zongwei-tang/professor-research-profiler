from fastapi import FastAPI

from app.api import analyze, history, professors, users

app = FastAPI(title="Professor Research Profiler")

app.include_router(professors.router)
app.include_router(analyze.router)
app.include_router(users.router)
app.include_router(history.router)
