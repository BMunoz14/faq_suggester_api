# --- filepath: app/api/routes.py ---
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.schemas import (
    Candidate,
    FeedbackRequest,
    HistoryItem,
    SuggestRequest,
    SuggestResponse,
)
from app.repository.history_repo import HistoryRepo
from app.services.faq_service import FaqService
from app.llm.question_generator import generate_next_question

router = APIRouter()


def get_faq_service(request: Request) -> FaqService:
    return request.app.state.faq_service  # type: ignore[attr-defined]


def get_history_repo(request: Request) -> HistoryRepo:
    return request.app.state.history_repo  # type: ignore[attr-defined]


@router.post("/suggest", response_model=SuggestResponse)
def suggest(
    payload: SuggestRequest,
    faq: FaqService = Depends(get_faq_service),
) -> SuggestResponse:
    candidates = faq.rank(payload.query, payload.k)
    if not candidates:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No suggestions found")
    return SuggestResponse(top_k=candidates, next_question=generate_next_question())


@router.get("/history", response_model=list[HistoryItem])
def history(repo: HistoryRepo = Depends(get_history_repo)):
    return repo.list()

@router.post("/feedback")
def feedback(
    payload: FeedbackRequest,
    faq: FaqService = Depends(get_faq_service),
    repo: HistoryRepo = Depends(get_history_repo),
):
    """Guarda la respuesta definitiva y amplía la base si distance ≥ threshold."""
    from datetime import datetime
    from app.config.settings import settings
    import json

    # 1) Persistir historial
    item = HistoryItem(
        query=payload.query,
        suggestion=payload.suggestion,
        timestamp=datetime.utcnow(),
        added=added,
    )
    repo.append(item)

    # 2) Aprendizaje activo
    added = False
    if payload.distance >= settings.DISTANCE_THRESHOLD:
        path = fq_path = faq.FAQ_PATH  # type: ignore[attr-defined]
        data = json.loads(path.read_text(encoding="utf-8"))
        data.append({"query": payload.query, "suggestion": payload.suggestion})
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

        # re-indexar solo este item
        new_id = f"faq-{len(data)-1}"
        emb = faq._embedder.embed_documents([payload.query])
        faq._collection.add(
            ids=[new_id],
            embeddings=emb,
            documents=[payload.query],
            metadatas=[{"suggestion": payload.suggestion}],
        )
        added = True
    return {"added": added}

