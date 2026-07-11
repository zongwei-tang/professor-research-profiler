import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    turso_db_url: str = os.environ.get("TURSO_DB_URL", "").removeprefix("libsql://")
    turso_db_token: str = os.environ.get("TURSO_DB_TOKENS", "")
    semantic_scholar_api_key: str = os.environ.get("SEMANTICS_SCHOLAR_API_KEY", "")
    deepseek_api_key: str = os.environ.get("DEEPSEEK_API_KEY", "")
    redis_host: str = os.environ.get("REDIS_HOST", "localhost")
    redis_port: int = int(os.environ.get("REDIS_PORT", 6379))
    redis_password: str = os.environ.get("REDIS_PASSWORD", "")
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.environ.get("JWT_EXPIRE_MINUTES", 60 * 24 * 7))


settings = Settings()
