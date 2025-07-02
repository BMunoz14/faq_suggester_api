# --- filepath: app/models/schemas.py ---
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, validator

# Request DTOs
class SuggestRequest(BaseModel):
    query: str = Field(..., description="Texto de la consulta")
    k: int = Field(3, ge=1, le=10, description="Número de sugerencias")

    @validator("query")
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be empty")
        return v.strip()

class FeedbackRequest(BaseModel):
    query: str
    suggestion: str
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Umbral de similitud")

    @validator("query", "suggestion")
    def _strip(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("string fields may not be blank")
        return v.strip()

# Response DTOs
class Candidate(BaseModel):
    suggestion: str
    distance: float

# Cambiar SuggestionItem a Candidate (son equivalentes)
SuggestionItem = Candidate  # Alias para mantener compatibilidad

class SuggestResponse(BaseModel):
    top_k: List[Candidate]
    suggestion: str
    next_question: str

class FeedbackResponse(BaseModel):
    added: bool

class HistoryItem(BaseModel):
    query: str
    suggestion: str
    next_question: str
    timestamp: datetime
    added: bool = False
