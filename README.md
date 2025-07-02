# --- filepath: README.md ---
# FAQ Suggester API

**Objetivo.** Proveer sugerencias automáticas a asesores de una alcaldía basadas en
preguntas frecuentes, con persistencia de historial y capacidad de crecer la base de
conocimiento.

## Ejecutar en local

La aplicación:

| Componente | Tecnología | Descripción |
|------------|------------|-------------|
| API REST   | **FastAPI + Uvicorn** | End-points  `POST /suggest`, `GET /history`, `POST /feedback`. |
| Búsqueda   | **ChromaDB** | Vector-store persistente con **OllamaEmbeddingFunction**. |
| Embeddings | **nomic-embed-text** | Modelo local de Ollama para generar vectores. |
| LLM        | **gemma3:12b** | Genera la siguiente pregunta simulada por el “ciudadano”. |
| Persistencia ligera | `data/faq.json` y `data/history.json` | No hay base de datos externa. |

---

## 1 · Demo en 3 comandos (Docker 🐳)

```bash
git clone https://github.com/tu-usuario/faq-suggester-api.git
cd faq-suggester-api
docker compose up --build
