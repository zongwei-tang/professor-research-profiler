import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    turso_db_url: str = os.environ.get("TURSO_DB_URL", "").removeprefix("libsql://")
    turso_db_token: str = os.environ.get("TURSO_DB_TOKENS", "")
    semantic_scholar_api_key: str = os.environ.get("SEMANTICS_SCHOLAR_API_KEY", "")
    deepseek_api_key: str = os.environ.get("DEEPSEEK_API_KEY", "")


settings = Settings()
