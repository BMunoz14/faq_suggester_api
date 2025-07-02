# FAQ Suggester API 🤖💬  
_Muestra sugerencias (suggest) de la base de conocimientos a partir de una pregunta (query)_

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.x-009688?logo=fastapi&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.0.x-673ab7)
![Ollama](https://img.shields.io/badge/Ollama-local-blue)
![Licence](https://img.shields.io/badge/Licence-MIT-green)


---

## 📍 Propósito

Automatizar la labor de los asesores que atienden solicitudes ciudadanas:

* **Recuperación inteligente** de la mejor respuesta entre las FAQ (con embeddings semánticos).
* **Aprendizaje activo** —si la similitud es baja— la nueva respuesta se agrega sin reiniciar el servicio.
* **Histórico auditable** de todas las consultas y respuestas enviadas.
* Sin base de datos externa: todo persiste en archivos JSON y un vector-store embebido.

---

## 🛠️ Tecnologías principales

| Capa | Tecnología | Rol |
|------|------------|-----|
| API REST | **FastAPI** + Uvicorn | End-points `/suggest`, `/history`, `/feedback` |
| Vector-store | **ChromaDB 1.x** | Almacena embeddings persistentes |
| Embeddings | **`nomic-embed-text`** (Ollama) | Conversión de texto → vector |
| LLM | **`gemma3:12b`** (Ollama) | Genera la “próxima pregunta” para pruebas |
| UI opcional | **Streamlit** | Chat + sugerencias + tabla de historial |
| Container | Docker & Docker Compose | Despliegue reproducible |

---

## 🚀 Instalación rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/BMunoz14/faq_suggester_api.git
cd faq_suggester_api

---

### 1 · Demo en 3 comandos (Docker 🐳)


```bash
git clone https://github.com/tu-usuario/faq-suggester-api.git
cd faq-suggester-api
docker compose up --build
