# Assignment Requirements Traceability

| Requirement | Implementation/evidence |
|---|---|
| Notebook management and isolation | `storage.py`, Notebooks tab |
| PDF/PPTX/TXT/web sources | `ingestion.py`, Sources tab |
| Extract, chunk, embed, vector store | `text_utils.py`, `vector_store.py`, persistent SQLite vectors |
| RAG chat grounded in sources | `rag.py`, Chat tab |
| Citations/source references | Numbered prompt context and retrieved-source list |
| Saved chat history | SQLite `messages` table |
| Report and quiz with answer key | `artifacts.py`, Artifacts tab |
| Persistent storage | SQLite, persistent Chroma, Render disk |
| UI and errors | Gradio `ui.py` and `gr.Error` validation |
| Two retrieval approaches | Similarity and MMR in `vector_store.py` |
| Evaluation of chunks/quality/time | Evaluation tab and `evaluation_template.md` |
| Cloud deployment and secrets | `Dockerfile`, `render.yaml`, `.env.example` |
| CI/CD | `.github/workflows/ci-cd.yml` |
| Short demo | `docs/demo_script.md` |
| Architecture document | `docs/architecture.md` |
