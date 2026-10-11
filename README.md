# NotebookLM / Gemini Notebook Clone

A full-stack, notebook-based study assistant that ingests documents and webpages, retrieves relevant evidence, answers with Gemini and citations, preserves notebook-specific state, and generates study artifacts.

## Required features implemented

- Notebook create, rename, delete, switch, and isolation
- PDF, PPTX, TXT, Markdown, and web URL ingestion
- Text extraction, overlapping chunks, local embeddings, and a persistent SQLite vector index
- Gemini RAG chat with inline source references and saved history
- Downloadable `report.md` and `quiz.md` with answer key
- SQLite persistence for metadata, chat, artifacts, and evaluation records
- Similarity and MMR retrieval comparison with timing
- Gradio UI with validation and user-facing errors
- Docker/Render deployment configuration and GitHub Actions CI/CD
- Architecture, evaluation, demonstration, and submission documentation

## Quick start

Prerequisites: Python 3.11+, Git, and a Gemini API key from Google AI Studio.

```bash
git clone YOUR_REPOSITORY_URL
cd notebooklm_clone_project
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install and configure:

```bash
pip install -r requirements.txt
cp .env.example .env
```

On Windows, use `Copy-Item .env.example .env` instead of `cp`. Open `.env`, replace `replace_with_your_key`, and then run:

```bash
python app.py
```

Open `http://localhost:7860`.

## Demonstrate the app locally

1. Create a notebook.
2. Upload `sample_sources/intro_to_rag.txt`.
3. Ask “How does RAG work?”
4. Confirm that the response contains bracketed citations and a retrieved-source list.
5. Generate the report and quiz and download both.
6. Compare similarity and MMR in the Evaluation tab.
7. Restart the app and confirm that notebooks, sources, and chat remain.

## Tests

```bash
pytest -q
python -m compileall app.py src scripts
```

## GitHub setup

Create an empty GitHub repository, then from this folder run:

```bash
git init
git add .
git commit -m "Complete NotebookLM clone"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If the screenshot repository already has a README or commit, clone that repository first and copy this project's contents into it, or reconcile the remote history before pushing.

## Deploy on Render

1. Push this repository to GitHub.
2. In Render, select **New → Blueprint** and connect the repository.
3. Render reads `render.yaml`; approve the web service and persistent disk.
4. In the service environment, add `GEMINI_API_KEY` with your real key.
5. Deploy and test the public URL.
6. In Render settings, create a deploy hook.
7. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
8. Name it `RENDER_DEPLOY_HOOK_URL` and paste the hook URL.
9. Push a small change and verify that GitHub Actions tests, builds, and triggers deployment.

Render's paid persistent disk is necessary for SQLite and Chroma persistence. If you choose Railway, AWS, Google Cloud Run, or another permitted platform, provide equivalent persistent storage and environment variables.

## Retrieval evaluation

The app implements two approaches:

| Approach | Behavior | Likely tradeoff |
|---|---|---|
| Similarity | Selects chunks closest to the query embedding | Focused and generally faster; may repeat similar evidence |
| MMR | Balances query relevance with diversity among selected chunks | Broader evidence; additional computation and sometimes less precise |

Run at least five questions in the Evaluation tab and complete `docs/evaluation_template.md` with actual chunk counts, response times, citation accuracy, and answer-quality ratings. Do not submit the placeholder evaluation as though it were measured data.

## Project structure

```text
app.py                         Application entry point
src/notebooklm_clone/          UI, ingestion, storage, RAG, and artifacts
tests/                         Automated unit tests
scripts/evaluate_rag.py        Optional command-line retrieval comparison
sample_sources/                Small source for smoke testing
docs/architecture.md           Architecture diagram and data flow
docs/evaluation_template.md    Required retrieval comparison worksheet
docs/demo_script.md            Required video plan
.github/workflows/ci-cd.yml    Test, container build, optional deploy trigger
Dockerfile / render.yaml       Cloud deployment
SUBMISSION_CHECKLIST.md        Final verification
```

## Known limitations and ethical notes

- This is a course-scale learning system, not a production security architecture.
- Scanned PDFs require OCR, which is not included.
- Some websites block automated extraction or render content only with JavaScript.
- Gemini output can still contain errors; citations should be checked against source chunks.
- Upload only documents you are authorized to process.

## Deliverable links

- Student: **YOUR NAME**
- GitHub repository: **ADD URL**
- Live deployment: **ADD URL**
- 1–2 minute demonstration: **ADD URL**

See `docs/architecture.md`, `docs/demo_script.md`, and `SUBMISSION_CHECKLIST.md` before submission.

