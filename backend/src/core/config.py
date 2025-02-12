from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = Field("/api/{API_VERSION}", validate_default=True)
    DEBUG: bool = False
    PROJECT_NAME: str = "Document Intelligence API"

    # Security
    SECRET_KEY: SecretStr
    ALLOWED_HOSTS: tuple[str, ...] = ("*",)

    # Vector Store
    PINECONE_API_KEY: SecretStr
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str

    EMBEDDING_MODEL: str
    CHAT_MODEL: str

    # Cache
    UPSTASH_REDIS_URL: str
    UPSTASH_REDIS_TOKEN: SecretStr
    CACHE_TTL: int = 3600  # 1 hour default

    # Google AI
    GOOGLE_API_KEY: SecretStr

    # Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: tuple[str, ...] = ("pdf",)

    @validator("API_PREFIX", pre=True)
    def assemble_api_prefix(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v.format(**values)
        return v

    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v: Path) -> Path:
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"
        use_enum_values = True
        extra = "forbid"
        str_strip_whitespace = True
        json_schema_extra = {}  # Add this to suppress the warning
        frozen = True  # Make settings immutable and hashable


_settings = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
