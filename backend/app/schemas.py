from pydantic import BaseModel, ConfigDict
from typing import Literal


class UserSignupRequest(BaseModel):
    username: str
    password: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfessorCandidate(BaseModel):
    authorId: str
    name: str
    affiliations: list[str] | None = None
    paperCount: int | None = None
    citationCount: int | None = None
    hIndex: int | None = None


class PaperFetchRequest(BaseModel):
    author_id: int
    author_name: str


class PaperCacheResponse(BaseModel):
    papers: list[dict]
    time: str | None


class AnalyzeRequest(BaseModel):
    author_id: int
    author_name: str
    interest: str
    language: Literal['English', 'Chinese']
    provider: Literal['anthropic', 'openai', 'deepseek', 'gemini']


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    user_id: int
    author_id: int
    author_name: str
    analysis_text: str
    time: str | None
    interest: str
    language: Literal['English', 'Chinese']
    provider: Literal['anthropic', 'openai', 'deepseek', 'gemini']
