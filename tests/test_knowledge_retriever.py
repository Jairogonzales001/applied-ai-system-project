import json

import pytest

from knowledge_retriever import KnowledgeRetriever


def test_retrieves_walk_guidance():
    retriever = KnowledgeRetriever()

    result = retriever.retrieve("walk", "Walk Max at 8 AM.")

    assert result.category == "walk"
    assert result.title == "Exercise Guidance"
    assert "walk" in result.tip.lower()
    assert result.confidence == 1.0


def test_retrieves_medication_safety_guidance():
    retriever = KnowledgeRetriever()

    result = retriever.retrieve("medication")

    assert result.category == "medication"
    assert "veterinarian" in result.tip.lower()
    assert "dosages" in result.tip.lower()


def test_unknown_category_uses_general_guidance():
    retriever = KnowledgeRetriever()

    result = retriever.retrieve("playtime")

    assert result.category == "other"
    assert result.confidence == 0.6


def test_missing_knowledge_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        KnowledgeRetriever(missing_file)


def test_invalid_json_raises_error(tmp_path):
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json}", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        KnowledgeRetriever(invalid_file)


def test_custom_knowledge_file(tmp_path):
    custom_file = tmp_path / "custom.json"
    custom_file.write_text(
        json.dumps(
            {
                "other": {
                    "title": "Custom Guidance",
                    "tip": "Custom test tip.",
                    "source": "Test source"
                }
            }
        ),
        encoding="utf-8",
    )

    retriever = KnowledgeRetriever(custom_file)
    result = retriever.retrieve("unknown")

    assert result.title == "Custom Guidance"
    assert result.source == "Test source"