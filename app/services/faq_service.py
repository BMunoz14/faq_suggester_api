import json
from pathlib import Path
from typing import List
from uuid import uuid4

from chromadb import PersistentClient
from langchain_ollama import OllamaEmbeddings
from app.config.settings import settings
from app.logging_config import logger

class FaqService:
    """Indexa FAQ con embeddings vía OllamaEmbeddings directamente"""
    
    def __init__(self, chroma_dir: str, faq_path: str, embeddings_model: str) -> None:
        # Usar OllamaEmbeddings directamente
        self.embedder = OllamaEmbeddings(model=embeddings_model)
        
        # Cliente y colección persistente
        self._client = PersistentClient(path=chroma_dir)
        self._collection = self._client.get_or_create_collection(
            name="faq_collection"
        )

        # Cargar e indexar si la colección está vacía
        self._data = self._load_faq(faq_path)
        if self._collection.count() == 0:
            self._index_faq()
        
        logger.info("Vectorstore inicializado con %d documentos", self._collection.count())

    # ------------------------------------------------------------------
    def _load_faq(self, faq_path: str) -> List[dict]:
        try:
            with open(faq_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error cargando FAQ: %s", str(e))
            return []

    def _index_faq(self) -> None:
        queries = [item["query"] for item in self._data]
        embeddings = self.embedder.embed_documents(queries)
        metas = [{"suggestion": item["suggestion"]} for item in self._data]
        ids = [str(uuid4()) for _ in queries]
        
        self._collection.add(
            documents=queries,
            embeddings=embeddings,
            metadatas=metas,
            ids=ids
        )
        self._client.persist()
        logger.info("Indexados %d documentos", len(queries))

    # ------------------------------------------------------------------
    def rank(self, query: str, k: int = 3) -> list:
        query_embedding = self.embedder.embed_query(query)
        res = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["metadatas", "distances"]
        )
        
        # Devuelve diccionarios en lugar de objetos Pydantic
        return [
            {"suggestion": meta["suggestion"], "distance": dist}
            for meta, dist in zip(res["metadatas"][0], res["distances"][0])
        ]

