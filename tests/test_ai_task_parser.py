import pytest

from ai_task_parser import parse_task_request


def test_parse_daily_walk():
    result = parse_task_request(
        "Walk Max every morning at 8 AM for 30 minutes.",
        known_pets=["Max", "Luna"],
    )

    assert result.pet_name == "Max"
    assert result.category == "walk"
    assert result.time == "08:00"
    assert result.frequency == "daily"
    assert result.duration_minutes == 30
    assert result.priority == "medium"
    assert result.is_complete is True


def test_medication_receives_high_priority():
    result = parse_task_request(
        "Give Luna her medication every day at 7:15 PM for 10 minutes.",
        known_pets=["Max", "Luna"],
    )

    assert result.pet_name == "Luna"
    assert result.category == "medication"
    assert result.time == "19:15"
    assert result.frequency == "daily"
    assert result.priority == "high"


def test_parser_reports_missing_time():
    result = parse_task_request(
        "Walk Max every morning.",
        known_pets=["Max"],
    )

    assert result.is_complete is False
    assert "task time" in result.missing_fields
    assert result.confidence < 1.0


def test_parser_reports_unknown_pet():
    result = parse_task_request(
        "Schedule grooming at 2 PM.",
        known_pets=["Max", "Luna"],
    )

    assert result.pet_name is None
    assert "pet name" in result.missing_fields


def test_parsed_result_creates_task():
    result = parse_task_request(
        "Feed Luna every day at 7 AM for 15 minutes.",
        known_pets=["Luna"],
    )

    task = result.to_task()

    assert task.time == "07:00"
    assert task.category == "feeding"
    assert task.frequency == "daily"
    assert task.duration_minutes == 15


def test_empty_request_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_task_request("")