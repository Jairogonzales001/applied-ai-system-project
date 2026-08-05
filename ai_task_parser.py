import re
from dataclasses import dataclass, field
from typing import Optional

from pawpal_system import Task


CATEGORY_KEYWORDS = {
    "medication": ["medication", "medicine", "pill", "dose"],
    "feeding": ["feed", "food", "breakfast", "dinner"],
    "walk": ["walk", "exercise", "run"],
    "appointment": ["appointment", "vet", "veterinarian", "checkup"],
    "grooming": ["groom", "brush", "bath", "nails"],
}

DEFAULT_DURATIONS = {
    "medication": 10,
    "feeding": 15,
    "walk": 30,
    "appointment": 60,
    "grooming": 30,
    "other": 30,
}

DESCRIPTION_BY_CATEGORY = {
    "medication": "Give medication",
    "feeding": "Feed pet",
    "walk": "Walk pet",
    "appointment": "Veterinary appointment",
    "grooming": "Groom pet",
    "other": "Pet care task",
}


@dataclass
class ParsedTask:
    """Structured result created from a natural-language request."""

    original_text: str
    pet_name: Optional[str]
    description: str
    time: Optional[str]
    frequency: str
    duration_minutes: int
    priority: str
    category: str
    confidence: float
    missing_fields: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Return True when enough information exists to create a task."""
        return not self.missing_fields

    def to_task(self) -> Task:
        """Convert the parsed result into a validated PawPal Task."""
        if not self.is_complete:
            missing = ", ".join(self.missing_fields)
            raise ValueError(
                f"Cannot create task because information is missing: {missing}."
            )

        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
        )


def parse_task_request(
    user_input: str,
    known_pets: Optional[list[str]] = None,
) -> ParsedTask:
    """
    Convert one natural-language pet-care request into structured task data.

    Example:
        Walk Max every morning at 8 AM for 30 minutes.
    """
    if not user_input or not user_input.strip():
        raise ValueError("Task request cannot be empty.")

    original_text = user_input.strip()
    normalized_text = original_text.lower()
    known_pets = known_pets or []

    category = _extract_category(normalized_text)
    pet_name = _extract_pet_name(original_text, known_pets, category)
    task_time = _extract_time(normalized_text)
    frequency = _extract_frequency(normalized_text)
    duration = _extract_duration(normalized_text, category)
    priority = _determine_priority(normalized_text, category)
    description = _create_description(original_text, category)

    missing_fields = []

    if not pet_name:
        missing_fields.append("pet name")

    if not task_time:
        missing_fields.append("task time")

    confidence = _calculate_confidence(
        pet_name=pet_name,
        task_time=task_time,
        category=category,
        missing_fields=missing_fields,
    )

    return ParsedTask(
        original_text=original_text,
        pet_name=pet_name,
        description=description,
        time=task_time,
        frequency=frequency,
        duration_minutes=duration,
        priority=priority,
        category=category,
        confidence=confidence,
        missing_fields=missing_fields,
    )


def _extract_category(text: str) -> str:
    """Classify the task using pet-care keywords."""
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "other"


def _extract_pet_name(
    original_text: str,
    known_pets: list[str],
    category: str,
) -> Optional[str]:
    """Find a pet name from the owner's known pets or the request text."""
    for pet_name in known_pets:
        if re.search(
            rf"\b{re.escape(pet_name)}\b",
            original_text,
            flags=re.IGNORECASE,
        ):
            return pet_name

    action_words = {
        "walk": r"\bwalk\s+([A-Za-z][A-Za-z'-]*)",
        "feeding": r"\bfeed\s+([A-Za-z][A-Za-z'-]*)",
        "medication": (
            r"\b(?:give|administer)\s+"
            r"([A-Za-z][A-Za-z'-]*)\s+"
            r"(?:his|her|their|the)?\s*(?:medication|medicine|pill)"
        ),
        "appointment": (
            r"\b(?:take|bring)\s+([A-Za-z][A-Za-z'-]*)\s+"
            r"(?:to|for)"
        ),
        "grooming": r"\b(?:groom|brush|bathe)\s+([A-Za-z][A-Za-z'-]*)",
    }

    pattern = action_words.get(category)

    if pattern:
        match = re.search(pattern, original_text, flags=re.IGNORECASE)

        if match:
            return match.group(1).title()

    return None


def _extract_time(text: str) -> Optional[str]:
    """Extract and normalize a time into 24-hour HH:MM format."""
    time_match = re.search(
        r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b",
        text,
        flags=re.IGNORECASE,
    )

    if not time_match:
        time_match = re.search(
            r"\b(\d{1,2}):(\d{2})\s*(am|pm)?\b",
            text,
            flags=re.IGNORECASE,
        )

    if not time_match:
        return None

    hour = int(time_match.group(1))
    minute_text = time_match.group(2)
    minute = int(minute_text) if minute_text is not None else 0
    meridiem = time_match.group(3)

    if minute > 59:
        return None

    if meridiem:
        if hour < 1 or hour > 12:
            return None

        if meridiem.lower() == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12
    elif hour > 23:
        return None

    return f"{hour:02d}:{minute:02d}"


def _extract_frequency(text: str) -> str:
    """Identify whether the task is one-time, daily, or weekly."""
    daily_phrases = [
        "daily",
        "every day",
        "every morning",
        "every afternoon",
        "every evening",
        "every night",
    ]

    weekly_phrases = [
        "weekly",
        "every week",
        "once a week",
    ]

    if any(phrase in text for phrase in daily_phrases):
        return "daily"

    if any(phrase in text for phrase in weekly_phrases):
        return "weekly"

    return "one-time"


def _extract_duration(text: str, category: str) -> int:
    """Extract task duration or use a category-specific default."""
    duration_match = re.search(
        r"\bfor\s+(\d+)\s*(?:minutes?|mins?)\b",
        text,
    )

    if duration_match:
        duration = int(duration_match.group(1))

        if duration > 0:
            return duration

    return DEFAULT_DURATIONS[category]


def _determine_priority(text: str, category: str) -> str:
    """Assign priority based on explicit language and task category."""
    if any(word in text for word in ["urgent", "important", "high priority"]):
        return "high"

    if any(word in text for word in ["low priority", "whenever"]):
        return "low"

    if category in {"medication", "appointment"}:
        return "high"

    return "medium"


def _create_description(original_text: str, category: str) -> str:
    """Create a concise task description."""
    description = DESCRIPTION_BY_CATEGORY[category]

    if category == "other":
        cleaned_text = re.sub(
            r"\bat\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b",
            "",
            original_text,
            flags=re.IGNORECASE,
        )

        cleaned_text = re.sub(
            r"\bfor\s+\d+\s*(?:minutes?|mins?)\b",
            "",
            cleaned_text,
            flags=re.IGNORECASE,
        ).strip(" .")

        if cleaned_text:
            return cleaned_text

    return description


def _calculate_confidence(
    pet_name: Optional[str],
    task_time: Optional[str],
    category: str,
    missing_fields: list[str],
) -> float:
    """Calculate a transparent confidence score for the parsed result."""
    confidence = 1.0

    if not pet_name:
        confidence -= 0.35

    if not task_time:
        confidence -= 0.35

    if category == "other":
        confidence -= 0.15

    if missing_fields:
        confidence -= 0.05

    return round(max(0.0, confidence), 2)