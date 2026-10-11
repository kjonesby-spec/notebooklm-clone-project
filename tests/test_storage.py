from src.notebooklm_clone.storage import Storage


def test_notebook_and_chat_persistence(tmp_path):
    storage = Storage(tmp_path / "test.db")
    notebook_id = storage.create_notebook("Robotics Notes")
    assert storage.list_notebooks()[0]["name"] == "Robotics Notes"
    storage.add_message(notebook_id, "user", "What is RAG?")
    storage.add_message(notebook_id, "assistant", "Retrieval augmented generation.", [{"number": 1}])
    messages = storage.list_messages(notebook_id)
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[1]["citations"][0]["number"] == 1


def test_delete_notebook_cascades(tmp_path):
    storage = Storage(tmp_path / "test.db")
    notebook_id = storage.create_notebook("Delete me")
    storage.add_source(notebook_id, "notes.txt", "txt", "notes.txt", 2)
    storage.delete_notebook(notebook_id)
    assert storage.list_notebooks() == []

