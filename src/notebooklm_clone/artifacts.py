from datetime import datetime, timezone
from pathlib import Path

from .config import ARTIFACTS_PATH
from .llm import generate


def _context(vector_store, notebook_id: str, limit=40) -> str:
    chunks = vector_store.all_chunks(notebook_id)[:limit]
    return "\n\n".join(f"SOURCE: {meta['source_name']}\n{text}" for text, meta in chunks)


def create_artifact(notebook_id, artifact_type, vector_store, storage):
    context = _context(vector_store, notebook_id)
    if not context:
        raise ValueError("Add a source before generating an artifact")
    if artifact_type == "report":
        instruction = "Create a concise Markdown study report with title, overview, key ideas, evidence, and conclusion. Cite source names."
        filename = "report.md"
    elif artifact_type == "quiz":
        instruction = "Create a 10-question Markdown quiz mixing multiple choice and short answer. Include a clearly separated answer key and source references."
        filename = "quiz.md"
    else:
        raise ValueError("Unknown artifact type")
    content = generate(f"{instruction}\n\nUse only this source material:\n{context}")
    folder = Path(ARTIFACTS_PATH) / notebook_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    header = f"<!-- Generated {datetime.now(timezone.utc).isoformat()} -->\n\n"
    path.write_text(header + content, encoding="utf-8")
    storage.add_artifact(notebook_id, artifact_type, filename, str(path))
    return str(path), content
