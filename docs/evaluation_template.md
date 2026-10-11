# Retrieval Evaluation

Five representative questions were used to compare similarity retrieval and maximum marginal relevance (MMR).

| Question | Method | Retrieved chunks | Response time | Citation accuracy (1–5) | Answer quality (1–5) | Notes |
|---|---|---:|---:|---:|---:|---|

| How does RAG improve factuality and reduce repeated evidence? | Similarity | 1 | 11.008 s | 5 | 5 | Accurate answer grounded in intro_to_rag.txt, chunk 0. |
| How does RAG improve factuality and reduce repeated evidence? | MMR | 1 | 8.603 s | 5 | 5 | Accurate, cited answer; faster in this run. |

| What happens to documents before they are stored in the vector database? | Similarity | 1 | 8.874 s | 5 | 5 | Correctly explained extraction, chunking, and embeddings. |
| What happens to documents before they are stored in the vector database? | MMR | 1 | 10.100 s | 5 | 5 | Same accurate and cited explanation; slower in this run. |

| How is a user question used to retrieve relevant information? | Similarity | 1 | 7.562 s | 5 | 5 | Correctly explained query embedding and retrieval with a valid citation. |
| How is a user question used to retrieve relevant information? | MMR | 1 | 8.849 s | 5 | 5 | Accurate cited answer explaining relevance and diversity. |

## Remaining Evaluation Questions

4. What is the difference between similarity retrieval and maximum marginal relevance (MMR)?
5. Why are citations useful in a RAG system?

## Selection Statement

The first two evaluations produced accurate, source-grounded answers with correct citations for both retrieval methods. Each method retrieved one chunk because the current notebook contains one short source document. Performance varied between runs: MMR was faster for the first question, while similarity was faster for the second. A final default-method selection will be made after all five questions are evaluated.