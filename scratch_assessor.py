import uuid
from typing import Any
from embeddings import VectorStore


class ScratchAssessor:
    """SCRATCH: Story Comprehension & Review Assessment Through Chat Highlights."""

    SCRATCH_DIMENSIONS = ["who", "what", "when", "where", "why", "how"]

    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self._sessions: dict[str, list[dict]] = {}

    def assess(self, session_id: str, book_id: str, message: str) -> dict[str, Any]:
        relevant = self.store.query_story(book_id, message, n=3)

        coverage_score = min(len(relevant) / 3.0, 1.0)
        comprehension_score = round(coverage_score * 100, 1)

        dimension_hits = self._detect_dimensions(message)

        self.store.store_chat(session_id, book_id, message, comprehension_score)
        self._sessions.setdefault(session_id, []).append({
            "message": message,
            "score": comprehension_score,
            "dimensions_hit": dimension_hits,
        })

        return {
            "session_id": session_id,
            "message": message,
            "comprehension_score": comprehension_score,
            "dimensions_covered": dimension_hits,
            "relevant_passages": relevant,
            "feedback": self._generate_feedback(comprehension_score, dimension_hits),
        }

    def get_session_score(self, session_id: str) -> dict[str, Any]:
        history = self._sessions.get(session_id, [])
        if not history:
            return {"session_id": session_id, "score": 0, "iterations": 0}
        avg = sum(h["score"] for h in history) / len(history)
        covered = set()
        for h in history:
            covered.update(h.get("dimensions_hit", []))
        return {
            "session_id": session_id,
            "average_score": round(avg, 1),
            "iterations": len(history),
            "dimensions_covered": list(covered),
            "dimensions_missing": [d for d in self.SCRATCH_DIMENSIONS if d not in covered],
        }

    def _detect_dimensions(self, text: str) -> list[str]:
        text_lower = text.lower()
        hits = []
        for dim in self.SCRATCH_DIMENSIONS:
            if dim in text_lower or any(w in text_lower for w in [
                "character", "event", "time", "place", "reason", "method"
            ]):
                hits.append(dim)
        return list(set(hits))

    @staticmethod
    def _generate_feedback(score: float, dims: list[str]) -> str:
        if score >= 80:
            return "Strong comprehension - you're engaging with core story elements."
        elif score >= 50:
            return f"Good start. Try addressing: {', '.join(set(['who', 'what', 'why']) - set(dims))}."
        else:
            return "Revisit the story. Focus on: who is involved, what happens, and why."
