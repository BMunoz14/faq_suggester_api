from langchain_ollama import ChatOllama
from app.config.settings import settings
from app.models.schemas import Candidate  # Importar Candidate para tipado

def generate_next_question(conversation_context: list, top_candidates: list) -> str:
    """Genera una pregunta de seguimiento usando el modelo local"""
    chat = ChatOllama(model=settings.LLM_MODEL, temperature=0.7)
    
    # Construir contexto de candidatos - CORRECCIÓN: Acceso por clave
    candidates_text = "\n".join([f"- {c['suggestion']}" for c in top_candidates])
    
    # Construir contexto de conversación
    convo_text = ""
    for i, item in enumerate(conversation_context[-3:]):
        convo_text += f"Turno {i+1}:\nUsuario: {item['query']}\nAsistente: {item['suggestion']}\n\n"
    
    prompt = (
        "Eres un asistente que genera preguntas de seguimiento relevantes. "
        "Basado en esta conversación reciente:\n"
        f"{convo_text}\n"
        "Y en estas sugerencias de respuestas:\n"
        f"{candidates_text}\n\n"
        "Genera EXACTAMENTE UNA pregunta natural para continuar la conversación. "
        "Responde solo con la pregunta, sin texto adicional."
    )
    
    return chat.invoke(prompt).content.strip()

