import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_KNOWLEDGE_PATH = Path(__file__).parent / "data" / "pet_care.json"


@dataclass
class RetrievedGuidance:
    """A pet-care knowledge item returned by the retriever."""

    category: str
    title: str
    tip: str
    source: str
    confidence: float


class KnowledgeRetriever:
    """Retrieves category-specific guidance from the PawPal knowledge base."""

    def __init__(self, knowledge_path: Path = DEFAULT_KNOWLEDGE_PATH):
        self.knowledge_path = Path(knowledge_path)
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> dict:
        """Load and validate the JSON knowledge base."""
        if not self.knowledge_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found: {self.knowledge_path}"
            )

        try:
            with self.knowledge_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError("Knowledge base contains invalid JSON.") from exc

        if not isinstance(data, dict):
            raise ValueError("Knowledge base must contain a JSON object.")

        return data

    def retrieve(
        self,
        category: str,
        query: Optional[str] = None,
    ) -> RetrievedGuidance:
        """
        Retrieve the most relevant guidance.

        The task category is the primary retrieval key. The original request
        may also be supplied for logging and future retrieval improvements.
        """
        normalized_category = (category or "other").lower().strip()

        if normalized_category in self.knowledge:
            selected_category = normalized_category
            confidence = 1.0
        else:
            selected_category = "other"
            confidence = 0.6

        item = self.knowledge[selected_category]

        return RetrievedGuidance(
            category=selected_category,
            title=item["title"],
            tip=item["tip"],
            source=item["source"],
            confidence=confidence,
        )