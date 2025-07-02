import unittest
import tempfile
import shutil
import os
from pathlib import Path
from fastapi.testclient import TestClient

# Importación relativa
from ..app.main import app

class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configurar entorno de prueba
        cls.temp_dir = tempfile.mkdtemp()
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
        
        # Crear datos de prueba
        cls.faq_path = Path(cls.temp_dir) / "faq.json"
        with open(cls.faq_path, 'w', encoding='utf-8') as f:
            json.dump([
                {"query": "Pregunta 1", "suggestion": "Respuesta 1"},
                {"query": "Pregunta 2", "suggestion": "Respuesta 2"}
            ], f)
        
        # Configurar environment variables
        os.environ["CHROMA_DIR"] = str(Path(cls.temp_dir) / "chroma_test_db")
        os.environ["FAQ_PATH"] = str(cls.faq_path)
        os.environ["EMBEDDINGS_MODEL"] = "nomic-embed-text"
        
        # Crear cliente de prueba
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def test_suggest_200(self):
        response = self.client.post("/suggest", json={"query": "Pregunta", "k": 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn("top_k", response.json())
        
    def test_history(self):
        # Primero crear algo de historial
        self.client.post("/suggest", json={"query": "Test", "k": 1})
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
        
    def test_feedback(self):
        response = self.client.post(
            "/feedback",
            json={"query": "Nueva pregunta", "suggestion": "Nueva respuesta", "threshold": 0.8}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("added", response.json())

if __name__ == "__main__":
    unittest.main()
