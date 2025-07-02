from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator

ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    API_TITLE: str = "FAQ Suggester API"
    API_VERSION: str = "0.1.0"

    # Modelos directamente sin URL
    LLM_MODEL: str = Field("gemma3:12b", env="LLM_MODEL")
    EMBEDDINGS_MODEL: str = Field("nomic-embed-text", env="EMBEDDINGS_MODEL")

    # Ruta al archivo de FAQs
    FAQ_PATH: Path = ROOT_DIR / "data" / "faq.json"

    HISTORY_FILE: Path = ROOT_DIR / "data" / "history.json"
    
    # ChromaDB
    CHROMA_DIR: Path = ROOT_DIR / "chroma_langchain_db"
    DISTANCE_THRESHOLD: float = Field(0.6, env="DISTANCE_THRESHOLD")

    @validator("DISTANCE_THRESHOLD")
    def _check(cls, v):
        if not 0.0 < v <= 1.0:
            raise ValueError("DISTANCE_THRESHOLD must be between 0 and 1")
        return v

settings = Settings()

