from pydantic import BaseModel, ConfigDict


class UserLoginRequest(BaseModel):
    username: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str


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
    user_id: int
    author_id: int
    author_name: str
    interest: str
    language: str
    provider: str


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    user_id: int
    author_id: int
    author_name: str
    analysis_text: str
    time: str | None
    interest: str
    language: str
    provider: str
