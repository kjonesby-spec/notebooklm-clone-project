import json
import sqlite3
from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import VECTOR_DATABASE_PATH


@lru_cache(maxsize=1)
def embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


class VectorStore:
    """Persistent vector index backed by SQLite and cosine similarity."""

    def __init__(self, path=VECTOR_DATABASE_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL,
                    source_id TEXT NOT NULL, source_name TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL, document TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )"""
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_vectors_notebook ON vectors(notebook_id)")

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def add_chunks(self, notebook_id, source_id, source_name, chunks):
        if not chunks:
            return
        embeddings = embedding_model().encode(chunks, normalize_embeddings=True)
        rows = [
            (f"{source_id}-{i}", notebook_id, source_id, source_name, i, text, json.dumps(vector.tolist()))
            for i, (text, vector) in enumerate(zip(chunks, embeddings))
        ]
        with self._connect() as db:
            db.executemany("INSERT OR REPLACE INTO vectors VALUES (?, ?, ?, ?, ?, ?, ?)", rows)

    def all_chunks(self, notebook_id):
        with self._connect() as db:
            rows = db.execute(
                "SELECT document, source_id, source_name, chunk_index FROM vectors WHERE notebook_id=? ORDER BY rowid",
                (notebook_id,),
            ).fetchall()
        return [
            (row["document"], {"source_id": row["source_id"], "source_name": row["source_name"], "chunk": row["chunk_index"]})
            for row in rows
        ]

    def retrieve(self, notebook_id, question, method="similarity", top_k=5):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM vectors WHERE notebook_id=?", (notebook_id,)).fetchall()
        if not rows:
            return []
        query = embedding_model().encode([question], normalize_embeddings=True)[0]
        vectors = np.asarray([json.loads(row["embedding"]) for row in rows], dtype=np.float32)
        scores = vectors @ query
        order = np.argsort(scores)[::-1]
        count = min(len(rows), max(int(top_k) * 3, int(top_k)))
        candidates = []
        for index in order[:count]:
            row = rows[int(index)]
            candidates.append({
                "text": row["document"],
                "metadata": {"source_id": row["source_id"], "source_name": row["source_name"], "chunk": row["chunk_index"]},
                "distance": float(1.0 - scores[index]),
                "vector": vectors[index],
            })
        if method == "similarity":
            selected = candidates[: int(top_k)]
        elif method == "mmr":
            selected = self._mmr(query, candidates, int(top_k))
        else:
            raise ValueError("Retrieval method must be similarity or mmr")
        for item in selected:
            item.pop("vector", None)
        return selected

    @staticmethod
    def _mmr(query, candidates, top_k, diversity=0.35):
        selected, remaining = [], list(range(len(candidates)))
        while remaining and len(selected) < top_k:
            best_index, best_score = None, -float("inf")
            for index in remaining:
                vector = candidates[index]["vector"]
                relevance = float(np.dot(query, vector))
                redundancy = max((float(np.dot(vector, candidates[j]["vector"])) for j in selected), default=0.0)
                score = (1 - diversity) * relevance - diversity * redundancy
                if score > best_score:
                    best_index, best_score = index, score
            selected.append(best_index)
            remaining.remove(best_index)
        return [candidates[index] for index in selected]

    def delete_notebook(self, notebook_id):
        with self._connect() as db:
            db.execute("DELETE FROM vectors WHERE notebook_id=?", (notebook_id,))
