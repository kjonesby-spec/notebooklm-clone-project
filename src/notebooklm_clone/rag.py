import time

from .llm import generate


def answer_question(notebook_id, question, vector_store, storage, method="similarity", top_k=5):
    started = time.perf_counter()
    matches = vector_store.retrieve(notebook_id, question, method=method, top_k=int(top_k))
    if not matches:
        return "Add at least one source before asking a question.", [], 0.0
    context_parts, citations = [], []
    for index, match in enumerate(matches, start=1):
        metadata = match["metadata"]
        context_parts.append(f"[{index}] {metadata['source_name']} (chunk {metadata['chunk']})\n{match['text']}")
        citations.append({"number": index, **metadata})
    prompt = f"""You are a source-grounded study assistant.
Answer only from the supplied context. If the answer is not present, say so.
Use inline citations such as [1] after every factual claim. Be concise but complete.

CONTEXT
{chr(10).join(context_parts)}

QUESTION
{question}
"""
    answer = generate(prompt)
    elapsed = time.perf_counter() - started
    source_list = "\n\n**Retrieved sources**\n" + "\n".join(
        f"- [{item['number']}] {item['source_name']}, chunk {item['chunk']}" for item in citations
    )
    final = answer + source_list
    storage.add_message(notebook_id, "user", question)
    storage.add_message(notebook_id, "assistant", final, citations)
    storage.add_evaluation(notebook_id, question, method, elapsed, f"Retrieved {len(matches)} chunks")
    return final, citations, elapsed

