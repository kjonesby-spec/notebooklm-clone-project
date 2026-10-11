import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .config import DATABASE_PATH


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Storage:
    def __init__(self, path: str | Path = DATABASE_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self):
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS notebooks (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sources (
                    id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, name TEXT NOT NULL,
                    kind TEXT NOT NULL, location TEXT, chunk_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, role TEXT NOT NULL,
                    content TEXT NOT NULL, citations_json TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, artifact_type TEXT NOT NULL,
                    name TEXT NOT NULL, path TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, question TEXT NOT NULL,
                    method TEXT NOT NULL, response_time REAL NOT NULL, result TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
                );
                """
            )

    def create_notebook(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Notebook name is required")
        notebook_id = str(uuid.uuid4())
        with self._connect() as db:
            db.execute("INSERT INTO notebooks VALUES (?, ?, ?)", (notebook_id, name, _now()))
        return notebook_id

    def list_notebooks(self):
        with self._connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM notebooks ORDER BY created_at DESC")]

    def rename_notebook(self, notebook_id: str, name: str):
        if not name.strip():
            raise ValueError("Notebook name is required")
        with self._connect() as db:
            db.execute("UPDATE notebooks SET name=? WHERE id=?", (name.strip(), notebook_id))

    def delete_notebook(self, notebook_id: str):
        with self._connect() as db:
            db.execute("DELETE FROM notebooks WHERE id=?", (notebook_id,))

    def add_source(self, notebook_id: str, name: str, kind: str, location: str, chunk_count: int) -> str:
        source_id = str(uuid.uuid4())
        with self._connect() as db:
            db.execute(
                "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?)",
                (source_id, notebook_id, name, kind, location, chunk_count, _now()),
            )
        return source_id

    def list_sources(self, notebook_id: str):
        with self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM sources WHERE notebook_id=? ORDER BY created_at DESC", (notebook_id,)
            )]

    def add_message(self, notebook_id: str, role: str, content: str, citations=None):
        with self._connect() as db:
            db.execute(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), notebook_id, role, content, json.dumps(citations or []), _now()),
            )

    def list_messages(self, notebook_id: str):
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM messages WHERE notebook_id=? ORDER BY created_at", (notebook_id,)
            )
        result = []
        for row in rows:
            item = dict(row)
            item["citations"] = json.loads(item.pop("citations_json"))
            result.append(item)
        return result

    def clear_messages(self, notebook_id: str):
        with self._connect() as db:
            db.execute("DELETE FROM messages WHERE notebook_id=?", (notebook_id,))

    def add_artifact(self, notebook_id: str, artifact_type: str, name: str, path: str):
        with self._connect() as db:
            db.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), notebook_id, artifact_type, name, path, _now()),
            )

    def list_artifacts(self, notebook_id: str):
        with self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM artifacts WHERE notebook_id=? ORDER BY created_at DESC", (notebook_id,)
            )]

    def add_evaluation(self, notebook_id: str, question: str, method: str, elapsed: float, result: str):
        with self._connect() as db:
            db.execute(
                "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), notebook_id, question, method, elapsed, result, _now()),
            )

    def list_evaluations(self, notebook_id: str):
        with self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM evaluations WHERE notebook_id=? ORDER BY created_at DESC", (notebook_id,)
            )]
