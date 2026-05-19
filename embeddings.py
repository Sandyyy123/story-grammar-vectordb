import uuid
from typing import Any
import chromadb
from chromadb.config import Settings


class VectorStore:
    """Manages story embeddings in ChromaDB."""

    def __init__(self, persist_path: str = "./.chromadb"):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_path,
            anonymized_telemetry=False,
        ))
        self.stories = self.client.get_or_create_collection("stories")
        self.sessions = self.client.get_or_create_collection("sessions")

    def store_story(self, book_id: str, story_grammar: dict[str, Any]) -> None:
        docs, ids, metas = [], [], []
        for dim in ["who", "what", "when", "where", "why", "how"]:
            for entry in story_grammar.get(dim, []):
                docs.append(entry["text"])
                ids.append(f"{book_id}_{dim}_{entry['page']}")
                metas.append({"book_id": book_id, "dimension": dim, "page": entry["page"]})
        if docs:
            self.stories.add(documents=docs, ids=ids, metadatas=metas)

    def query_story(self, book_id: str, query_text: str, n: int = 5) -> list[dict]:
        results = self.stories.query(
            query_texts=[query_text],
            n_results=n,
            where={"book_id": book_id},
        )
        return results.get("documents", [[]])[0]

    def store_chat(self, session_id: str, book_id: str, message: str, score: float) -> None:
        self.sessions.add(
            documents=[message],
            ids=[str(uuid.uuid4())],
            metadatas=[{"session_id": session_id, "book_id": book_id, "score": score}],
        )

    def get_story_summary(self, book_id: str) -> dict | None:
        results = self.stories.get(where={"book_id": book_id})
        if not results["ids"]:
            return None
        dims: dict[str, list] = {}
        for doc, meta in zip(results["documents"], results["metadatas"]):
            d = meta["dimension"]
            dims.setdefault(d, []).append({"page": meta["page"], "text": doc})
        return {"book_id": book_id, "grammar": dims}
