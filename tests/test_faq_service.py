import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path

# Importación relativa
from ..app.services.faq_service import FaqService

class TestFaqService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Crear directorio temporal
        cls.temp_dir = tempfile.mkdtemp()
        cls.chroma_dir = Path(cls.temp_dir) / "chroma_test_db"
        cls.faq_path = Path(cls.temp_dir) / "faq.json"
        
        # Crear datos de prueba
        test_data = [
            {"query": "¿Cómo cambio mi contraseña?", "suggestion": "Visita la configuración..."},
            {"query": "¿Dónde veo mi historial?", "suggestion": "En el menú principal..."}
        ]
        
        with open(cls.faq_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        self.svc = FaqService(
            chroma_dir=str(self.chroma_dir),
            faq_path=str(self.faq_path),
            embeddings_model="nomic-embed-text"
        )

    def test_rank_returns_correct_number(self):
        res = self.svc.rank("contraseña", k=1)
        self.assertEqual(len(res), 1)
        
    def test_rank_structure(self):
        res = self.svc.rank("historial", k=1)
        self.assertIn("suggestion", res[0])
        self.assertIn("distance", res[0])
        self.assertIsInstance(res[0]["distance"], float)

if __name__ == "__main__":
    unittest.main()
