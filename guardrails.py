import re
from dataclasses import dataclass, field


@dataclass
class GuardrailResult:
    """Result of checking a user request for unsafe content."""

    allowed: bool
    message: str
    matched_rules: list[str] = field(default_factory=list)


class Guardrails:
    """Blocks unsafe veterinary advice while allowing scheduling requests."""

    DOSAGE_PATTERNS = [
        r"\bhow much\b",
        r"\bwhat dose\b",
        r"\bwhat dosage\b",
        r"\bhow many mg\b",
        r"\b\d+\s*milligrams?\b",
        r"\b\d+\s*mg\b",
        r"\bmg of\b",
    ]

    DIAGNOSIS_PATTERNS = [
        r"\bdiagnose\b",
        r"\bwhat disease\b",
        r"\bwhat illness\b",
        r"\bwhat is wrong with\b",
    ]

    TREATMENT_PATTERNS = [
        r"\bwhat medicine should\b",
        r"\bwhat medication should\b",
        r"\bcan you prescribe\b",
        r"\bplease prescribe\b",
        r"\bprescribe\s+(?:a|some|the)?\s*(?:medicine|medication|treatment)\b",
        r"\bhow should i treat\b",
        r"\bhow do i treat\b",
        r"\btreat my\b",
        r"\bcure my\b",
    ]

    HUMAN_MEDICATIONS = [
        r"\bibuprofen\b",
        r"\btylenol\b",
        r"\bacetaminophen\b",
        r"\baspirin\b",
        r"\bnaproxen\b",
    ]

    def check(self, user_input: str) -> GuardrailResult:
        """Check whether a request is safe for PawPal to process."""

        if not user_input or not user_input.strip():
            return GuardrailResult(
                allowed=False,
                message="Please enter a pet-care scheduling request.",
                matched_rules=["empty_input"],
            )

        normalized = user_input.lower().strip()
        matched_rules = []

        if self._matches_any(normalized, self.DOSAGE_PATTERNS):
            matched_rules.append("medication_dosage")

        if self._matches_any(normalized, self.DIAGNOSIS_PATTERNS):
            matched_rules.append("medical_diagnosis")

        if self._matches_any(normalized, self.TREATMENT_PATTERNS):
            matched_rules.append("treatment_recommendation")

        if self._matches_any(normalized, self.HUMAN_MEDICATIONS):
            matched_rules.append("human_medication")

        if matched_rules:
            return GuardrailResult(
                allowed=False,
                message=(
                    "PawPal can schedule care tasks, but it cannot provide "
                    "medication dosages, diagnoses, or treatment recommendations. "
                    "Please contact a licensed veterinarian."
                ),
                matched_rules=matched_rules,
            )

        return GuardrailResult(
            allowed=True,
            message="Request passed safety checks.",
        )

    @staticmethod
    def _matches_any(text: str, patterns: list[str]) -> bool:
        """Return True when any regular-expression pattern matches the text."""
        return any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for pattern in patterns
        )