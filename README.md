# Story Grammar VectorDB PoC

A proof-of-concept for SCRATCH (Story Comprehension & Review Assessment Through Chat Highlights) using VectorDB embeddings.

## Architecture
- FastAPI REST API
- OpenAI/sentence-transformers for embeddings
- ChromaDB (local) / Pinecone (AWS) for vector storage
- 5W1H narrative flow extraction from book JSON
- Persistent chat iteration tracking

## Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints
- `POST /upload-book` — Parse book JSON, extract story grammar, store embeddings
- `POST /chat` — Submit chat iteration, assess against SCRATCH baseline
- `GET /story-summary/{book_id}` — Get extracted narrative structure
- `GET /assessment/{session_id}` — Get comprehension score for a session
