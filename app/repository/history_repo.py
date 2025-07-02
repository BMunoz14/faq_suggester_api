# --- filepath: app/repository/history_repo.py ---
import json
from datetime import datetime
from pathlib import Path
from typing import List

from filelock import FileLock

from app.config.settings import settings
from app.logging_config import logger
from app.models.schemas import HistoryItem

HISTORY_PATH = Path(__file__).resolve().parents[2] / "data" / "history.json"
LOCK_PATH = HISTORY_PATH.with_suffix(".lock")


class HistoryRepo:
    """Persistencia simple en archivo JSON."""

    def __init__(self) -> None:
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not HISTORY_PATH.exists():
            HISTORY_PATH.write_text("[]", encoding="utf-8")

    def _read_all(self) -> List[dict]:
        with FileLock(str(LOCK_PATH)):
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))

    def list(self) -> List[HistoryItem]:
        return [HistoryItem(**rec) for rec in self._read_all()]

    def append(self, record: HistoryItem) -> None:
        with FileLock(str(LOCK_PATH)):
            data = self._read_all()
            data.append(record.dict())
            HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            logger.debug("History saved (%d items)", len(data))
