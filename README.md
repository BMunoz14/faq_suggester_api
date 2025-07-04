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

## 📁 Estructura del Proyecto

```text
📁faq_suggester_api/
├── 📁app/                        # Código de la API FastAPI
│   ├── 📁api/
│   │   ├── __init__.py
│   │   └── routes.py             # Endpoints: /suggest, /history, /feedback
│   ├── 📁config/
│   │   ├── __init__.py
│   │   └── settings.py           # Variables de entorno y paths
│   ├── 📁llm/
│   │   ├── __init__.py
│   │   └── question_generator.py
│   ├── 📁models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── 📁repository/
│   │   ├── __init__.py
│   │   └── history_repo.py
│   ├── 📁services/
│   │   ├── __init__.py
│   │   └── faq_service.py
│   ├── 📁logging_config.py
│   └── __init__.py
│
├── 📁chroma_langchain_db/        # Vector-store persistente (Chroma)
│   └── ...                       # Archivos creados en tiempo de ejecución
│
├── 📁data/                       # Base de conocimiento & historial
│   ├── faq.json
│   └── history.json
│
├── 📁prompts/                     # Plantillas de prompts auxiliares
│   └── question_generator_system.txt
│
├── 📁tests/                       # Pruebas unitarias / integración
│   ├── __init__.py
│   ├── test_faq_service.py
│   └── test_routes.py
│
├── 📁ui/                         # Cliente Streamlit (opcional)
│   └── streamlit_app.py
│
├── main.py                       # Wrapper / entry-point
├── Dockerfile                    # Build de la imagen (API + UI)
├── docker-compose.yml            # Orquestación: API, UI, Ollama…
├── Makefile                      # Atajos para lint, test, build…
├── pyproject.toml                # Dependencias (uv / PDM / Poetry)
├── uv.lock                       # Lockfile reproducible para uv
├── requirements.txt              # Sólo para la imagen Docker slim
├── .python-version               # Versión fijada (pyenv)
└── .gitignore                    # Reglas globales
```

---

## 🎯 Prerequisitos
Antes de iniciar el proyecto, asegúrate de tener instalado lo siguiente:

- **uv**: Un administrador de paquetes de Python rápido, escrito en Rust. Lo usaremos para gestionar las dependencias del proyecto.
  Sitio web oficial: [https://docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Ollama**: Una herramienta para ejecutar modelos de lenguaje grandes localmente. Necesitarás descargar e instalar Ollama para poder usar los modelos de IA.
  Sitio web oficial: [Ollama](https://ollama.com/)
- **Chocolatey** (Solo para Windows): Un administrador de paquetes para Windows. Si usas Windows, Chocolatey facilita la instalación de herramientas como make.
  Sitio web oficial: [Chocolatey](https://chocolatey.org/install)
- **make**: Una utilidad que controla la generación de ejecutables y otros archivos a partir de los archivos fuente de un programa. Lo usaremos para simplificar el proceso de inicio del proyecto.

---

## 🚀 Instalación

### 1. 🤖 Tener un modelo de IA disponible

Necesitas tener corriendo **Ollama local**
Instala un LLM en local con el siguiente comando para **nomic-embed-text**
```bash
ollama run gemma3:12b
```
Instala un modelo de embeddings en local con el siguiente comando para **gemma3:12b**
```bash
ollama pull nomic-embed-text
```
Listo ya tienes lista una gran parte del trabajo, ahora puedes desde tu terminal ver los modelos disponibles con:
```bash
ollama list
```

### 2. Demo en 3 comandos (con Docker Compose 🐳)

```bash
git clone https://github.com/BMunoz14/faq_suggester_api.git
cd faq-suggester-api
docker compose up --build
```

### 3. Segunda opcion Demo en local (sin Docker)

Clona el repositorio
```bash
git clone https://github.com/BMunoz14/faq_suggester_api.git
cd faq-suggester-api
```
Instalar dependencias con **uv**
```bash
uv sync
```
Ejecuta desde la terminal ubicándose en el proyecto **Para iniciar la API REST**
```bash
make dev
```
Opcional si quieres probar desde el navegador en `http://localhost:8501/`, abre otra terminal en el proyecto y ejecuta **Para probar la API desde Streamlit**
```bash
make web
```
![image](https://github.com/user-attachments/assets/aeb8c7da-cc19-4954-ae69-02e6c6ab114b)

---

## faq_suggester_api funcionando

### API Swagger en `http://localhost:8000/docs`

POST /suggest
![image](https://github.com/user-attachments/assets/a7794559-0b76-418d-9101-d7d07d6fed9a)

GET /history
![image](https://github.com/user-attachments/assets/caaaebf9-533f-44be-af15-eeb9243746dd)

POST /feedback
![image](https://github.com/user-attachments/assets/11c0588a-e9b8-4289-9497-a1c3d2ca77bb)

### API desde Streamlit `(http://localhost:8501)`

![image](https://github.com/user-attachments/assets/9e508760-1850-460c-970e-76db2a5dab28)

![image](https://github.com/user-attachments/assets/ac32a377-090e-42d5-9e35-148d4cc93d9c)

---
