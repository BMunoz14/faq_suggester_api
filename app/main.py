import os
import json
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_ollama import ChatOllama
from chromadb import PersistentClient
from chromadb.utils import embedding_functions

from app.config.settings import settings
from app.models.schemas import (
    SuggestRequest, Candidate, SuggestResponse,
    FeedbackRequest, FeedbackResponse, HistoryItem
)
from app.services.faq_service import FaqService
from app.llm.question_generator import generate_next_question

# Deshabilitar telemetría de ChromaDB
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"

app = FastAPI(
    title="RAG FAQ Service",
    description="API RESTful con ChromaDB y ChatOllama",
    version="0.1.0"
)

# Inicializar servicios
#faq_service = FaqService()
faq_service = FaqService(
    chroma_dir=str(settings.CHROMA_DIR),
    faq_path=str(settings.FAQ_PATH),
    embeddings_model=settings.EMBEDDINGS_MODEL,
)

# Función para extraer JSON de la respuesta
def extract_json(response: str) -> dict:
    """Extrae un objeto JSON de una cadena, eliminando texto adicional"""
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("No se encontró JSON válido en la respuesta")

# Ruta para el archivo de historial
HISTORY_FILE = settings.HISTORY_FILE

def load_history() -> list:
    """Carga el historial desde el archivo JSON"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history: list):
    """Guarda el historial en el archivo JSON"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

@app.post("/suggest", response_model=SuggestResponse)
async def suggest(req: SuggestRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="'query' no puede estar vacío.")
    
    if req.k <= 0 or req.k > 10:
        raise HTTPException(status_code=400, detail="'k' debe estar entre 1 y 10")

    # Obtener top-k de la colección
    candidates = faq_service.rank(req.query, req.k)
    
    if not candidates:
        raise HTTPException(status_code=404, detail="No se encontraron sugerencias")
    
    # Preparar top_k para el prompt - CORRECCIÓN: Acceso por clave
    top_k_for_prompt = [
        {"suggestion": c["suggestion"], "distance": c["distance"]}
        for c in candidates
    ]
    
    # Configurar LLM para generar respuesta
    llm = ChatOllama(
        model=settings.LLM_MODEL,
        temperature=0.8,
        num_predict=256
    )
    
    # Preparar prompt estructurado
    prompt = f"""
    Eres un asistente de FAQ que responde consultas basado en un contexto.
    Tu respuesta DEBE ser un JSON válido con las siguientes claves:
    - "suggestion": Resumen conciso de la respuesta basado en el contexto
    - "next_question": Una sola pregunta de seguimiento relevante

    Contexto (Top {req.k} sugerencias):
    {json.dumps(top_k_for_prompt, indent=2)}

    Consulta del usuario:
    {req.query}

    Instrucciones:
    1. Usa SOLAMENTE la información del contexto
    2. Genera EXCLUSIVAMENTE un objeto JSON válido
    3. No incluyas texto adicional fuera del JSON
    """
    
    # Construir mensajes para ChatOllama
    messages = [{"role": "system", "content": prompt}]
    
    # Llamada al LLM
    try:
        response = llm.invoke(messages)
        content = response.content
        
        # Extraer y validar JSON
        data = extract_json(content)
    except Exception as e:
        error_detail = f"Error en generación de respuesta: {str(e)}"
        if content:
            error_detail += f"\nRespuesta LLM: {content[:500]}"
        raise HTTPException(status_code=500, detail=error_detail)
    
    # Validar estructura de respuesta
    required_keys = {"suggestion", "next_question"}
    if not all(key in data for key in required_keys):
        error_detail = f"Estructura de respuesta inválida. Claves esperadas: {required_keys}\nRecibido: {list(data.keys())}"
        raise HTTPException(status_code=500, detail=error_detail)

    # Generar pregunta de seguimiento adicional con contexto
    try:
        history = load_history()
        next_question = generate_next_question(
            conversation_context=history[-3:],
            top_candidates=candidates 
        )
    except Exception:
        next_question = data["next_question"]

    # Guardar en historial
    history_item = {
        "query": req.query,
        "suggestion": data["suggestion"],
        "next_question": next_question,
        "timestamp": datetime.now().isoformat()
    }
    
    history = load_history()
    history.append(history_item)
    save_history(history)
    
    # Preparar respuesta - CORRECCIÓN: Crear objetos Candidate
    top_k_response = [
        Candidate(suggestion=c["suggestion"], distance=c["distance"])
        for c in candidates
    ]
    
    return SuggestResponse(
        top_k=top_k_response,
        suggestion=data["suggestion"],
        next_question=next_question
    )

@app.get("/history", response_model=list[HistoryItem])
async def get_history():
    """Obtiene el historial completo de conversaciones"""
    return load_history()

@app.post("/feedback", response_model=FeedbackResponse)
async def feedback(req: FeedbackRequest):
    """Recibe feedback y agrega nuevo documento si es necesario"""
    # Obtener la consulta más similar
    candidates = faq_service.rank(req.query, 1)
    
    if not candidates:
        return FeedbackResponse(added=False)
    
    # Calcular similitud (1 - distancia)
    similarity = 1 - candidates[0]["distance"]
    
    added = False
    if similarity < req.threshold:
        # Agregar nuevo documento a ChromaDB
        new_id = str(uuid4())
        faq_service._collection.add(
            documents=[req.query],
            metadatas=[{"suggestion": req.suggestion}],
            ids=[new_id]
        )
        faq_service._client.persist()
        added = True
    
    return FeedbackResponse(added=added)

