import re
from typing import Any


class BookParser:
    """Parse book JSON and extract 5W1H story grammar elements."""

    W1H_PROMPTS = {
        "who": ["character", "protagonist", "antagonist", "person", "hero"],
        "what": ["event", "action", "conflict", "plot", "climax"],
        "when": ["time", "period", "year", "day", "moment", "scene"],
        "where": ["location", "place", "setting", "city", "world"],
        "why": ["reason", "motivation", "cause", "goal", "desire"],
        "how": ["method", "solution", "resolution", "outcome", "consequence"],
    }

    def extract_story_grammar(self, book_data: dict[str, Any]) -> dict:
        pages = book_data.get("pages", [])
        narrative = {
            "who": [],
            "what": [],
            "when": [],
            "where": [],
            "why": [],
            "how": [],
            "structure": {
                "beginning": [],
                "rising_action": [],
                "climax": [],
                "resolution": [],
            },
            "relationships": [],
            "themes": [],
        }

        total = len(pages)
        for i, page in enumerate(pages):
            text = page.get("text", "") + " " + page.get("caption", "")
            text_lower = text.lower()
            position = i / max(total, 1)

            for dim, keywords in self.W1H_PROMPTS.items():
                for kw in keywords:
                    if kw in text_lower and text.strip():
                        entry = {"page": i + 1, "text": text[:200].strip()}
                        if entry not in narrative[dim]:
                            narrative[dim].append(entry)
                            break

            if position < 0.2:
                narrative["structure"]["beginning"].append({"page": i + 1, "text": text[:100]})
            elif position < 0.6:
                narrative["structure"]["rising_action"].append({"page": i + 1, "text": text[:100]})
            elif position < 0.8:
                narrative["structure"]["climax"].append({"page": i + 1, "text": text[:100]})
            else:
                narrative["structure"]["resolution"].append({"page": i + 1, "text": text[:100]})

        return narrative
