"""Run a small command-line comparison of similarity and MMR retrieval."""
import argparse
import json
import time

from src.notebooklm_clone.vector_store import VectorStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook_id")
    parser.add_argument("question")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    store = VectorStore()
    for method in ("similarity", "mmr"):
        started = time.perf_counter()
        matches = store.retrieve(args.notebook_id, args.question, method, args.top_k)
        print(json.dumps({"method": method, "seconds": time.perf_counter() - started, "matches": matches}, indent=2))


if __name__ == "__main__":
    main()
