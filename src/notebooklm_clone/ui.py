import os
from pathlib import Path

import gradio as gr

from .artifacts import create_artifact
from .config import PORT
from .ingestion import extract_file, extract_url
from .rag import answer_question
from .storage import Storage
from .text_utils import chunk_text
from .vector_store import VectorStore


storage = Storage()
vectors = VectorStore()


def _choices():
    return [(row["name"], row["id"]) for row in storage.list_notebooks()]


def _require(notebook_id):
    if not notebook_id:
        raise gr.Error("Create or select a notebook first.")
    return notebook_id


def create_notebook(name):
    try:
        notebook_id = storage.create_notebook(name)
        return gr.update(choices=_choices(), value=notebook_id), notebook_id, "Notebook created."
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def select_notebook(notebook_id):
    if not notebook_id:
        return None, [], [], [], "No notebook selected."
    messages = [{"role": item["role"], "content": item["content"]} for item in storage.list_messages(notebook_id)]
    return notebook_id, storage.list_sources(notebook_id), messages, storage.list_artifacts(notebook_id), "Notebook loaded."


def rename_notebook(notebook_id, name):
    try:
        storage.rename_notebook(_require(notebook_id), name)
        return gr.update(choices=_choices(), value=notebook_id), "Notebook renamed."
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def delete_notebook(notebook_id):
    notebook_id = _require(notebook_id)
    vectors.delete_notebook(notebook_id)
    storage.delete_notebook(notebook_id)
    return gr.update(choices=_choices(), value=None), None, [], [], [], "Notebook deleted."


def add_files(notebook_id, files):
    notebook_id = _require(notebook_id)
    if not files:
        raise gr.Error("Choose at least one file.")
    results = []
    for file_path in files:
        name, text = extract_file(file_path)
        chunks = chunk_text(text)
        source_id = storage.add_source(notebook_id, name, Path(file_path).suffix.lower(), str(file_path), len(chunks))
        vectors.add_chunks(notebook_id, source_id, name, chunks)
        results.append(f"{name}: {len(chunks)} chunks")
    return storage.list_sources(notebook_id), "Added " + "; ".join(results)


def add_webpage(notebook_id, url):
    notebook_id = _require(notebook_id)
    name, text = extract_url(url)
    chunks = chunk_text(text)
    source_id = storage.add_source(notebook_id, name, "url", url, len(chunks))
    vectors.add_chunks(notebook_id, source_id, name, chunks)
    return storage.list_sources(notebook_id), f"Added {name} with {len(chunks)} chunks."


def ask(notebook_id, question, history, method, top_k):
    notebook_id = _require(notebook_id)
    if not question.strip():
        raise gr.Error("Enter a question.")
    answer, _, elapsed = answer_question(notebook_id, question, vectors, storage, method, top_k)
    history = (history or []) + [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
    return "", history, f"Answered in {elapsed:.2f} seconds using {method}."


def clear_chat(notebook_id):
    storage.clear_messages(_require(notebook_id))
    return [], "Chat history cleared."


def make_artifact(notebook_id, artifact_type):
    try:
        path, content = create_artifact(_require(notebook_id), artifact_type, vectors, storage)
        return content, path, storage.list_artifacts(notebook_id), f"Created {Path(path).name}."
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def compare_retrieval(notebook_id, question, top_k):
    notebook_id = _require(notebook_id)
    rows = []
    for method in ("similarity", "mmr"):
        answer, citations, elapsed = answer_question(notebook_id, question, vectors, storage, method, top_k)
        rows.append({
            "method": method, "seconds": round(elapsed, 3), "chunks": len(citations),
            "answer_preview": answer[:400],
        })
    return rows, "Compare coverage, repetition, citations, and response time; record your conclusion in docs/evaluation_template.md."


def build_app():
    with gr.Blocks(title="NotebookLM Clone") as app:
        gr.Markdown("# NotebookLM Clone\nA notebook-based, source-grounded Gemini study assistant.")
        selected = gr.State(None)
        status = gr.Markdown("Create or select a notebook to begin.")

        with gr.Tab("1. Notebooks"):
            notebook_dropdown = gr.Dropdown(label="Current notebook", choices=_choices())
            with gr.Row():
                notebook_name = gr.Textbox(label="Notebook name")
                create_button = gr.Button("Create", variant="primary")
                rename_button = gr.Button("Rename")
                delete_button = gr.Button("Delete", variant="stop")

        with gr.Tab("2. Sources"):
            uploads = gr.File(label="Upload PDF, PPTX, TXT, or MD", file_count="multiple", type="filepath")
            upload_button = gr.Button("Process files", variant="primary")
            with gr.Row():
                url = gr.Textbox(label="Web URL")
                url_button = gr.Button("Add webpage")
            sources_table = gr.JSON(label="Notebook sources")

        with gr.Tab("3. Chat"):
            chatbot = gr.Chatbot(type="messages", height=430)
            question = gr.Textbox(label="Ask about your sources", placeholder="What are the main ideas?")
            with gr.Row():
                method = gr.Radio(["similarity", "mmr"], value="similarity", label="Retrieval")
                top_k = gr.Slider(2, 10, value=5, step=1, label="Chunks")
            with gr.Row():
                ask_button = gr.Button("Ask", variant="primary")
                clear_button = gr.Button("Clear chat")

        with gr.Tab("4. Artifacts"):
            artifact_type = gr.Radio(["report", "quiz"], value="report", label="Artifact")
            artifact_button = gr.Button("Generate artifact", variant="primary")
            artifact_preview = gr.Markdown()
            artifact_download = gr.File(label="Download")
            artifacts_table = gr.JSON(label="Saved artifacts")

        with gr.Tab("5. Evaluation"):
            eval_question = gr.Textbox(label="Evaluation question")
            eval_button = gr.Button("Compare similarity and MMR", variant="primary")
            eval_table = gr.JSON(label="Comparison")

        create_button.click(create_notebook, notebook_name, [notebook_dropdown, selected, status])
        notebook_dropdown.change(select_notebook, notebook_dropdown, [selected, sources_table, chatbot, artifacts_table, status])
        rename_button.click(rename_notebook, [selected, notebook_name], [notebook_dropdown, status])
        delete_button.click(delete_notebook, selected, [notebook_dropdown, selected, sources_table, chatbot, artifacts_table, status])
        upload_button.click(add_files, [selected, uploads], [sources_table, status])
        url_button.click(add_webpage, [selected, url], [sources_table, status])
        ask_button.click(ask, [selected, question, chatbot, method, top_k], [question, chatbot, status])
        question.submit(ask, [selected, question, chatbot, method, top_k], [question, chatbot, status])
        clear_button.click(clear_chat, selected, [chatbot, status])
        artifact_button.click(make_artifact, [selected, artifact_type], [artifact_preview, artifact_download, artifacts_table, status])
        eval_button.click(compare_retrieval, [selected, eval_question, top_k], [eval_table, status])
    original_launch = app.launch
    app.launch = lambda **kwargs: original_launch(
        server_name="0.0.0.0", server_port=PORT, show_error=True, **kwargs
    )
    return app
