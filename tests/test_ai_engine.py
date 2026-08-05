from ai_engine import AIEngine
from pawpal_system import Owner, Pet, Task


def create_owner():
    """Create a reusable owner with two pets for AI engine tests."""
    owner = Owner("Jairo")
    owner.add_pet(Pet("Max", "Dog"))
    owner.add_pet(Pet("Luna", "Cat"))
    return owner


def test_engine_creates_task():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Walk Max every morning at 8 AM for 30 minutes."
    )

    assert response.success is True
    assert response.task_created is True
    assert response.pet_name == "Max"
    assert response.created_task is not None
    assert response.created_task.category == "walk"
    assert response.created_task.time == "08:00"
    assert len(owner.pets[0].tasks) == 1


def test_engine_requests_missing_information():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request("Walk Max every morning.")

    assert response.success is False
    assert response.task_created is False
    assert response.parsed_task is not None
    assert "task time" in response.message.lower()


def test_engine_rejects_empty_request():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request("")

    assert response.success is False
    assert response.task_created is False
    assert (
        "please enter a pet-care scheduling request"
        in response.message.lower()
    )
    assert response.logs[-1] == "Guardrail blocked request: empty_input"


def test_engine_detects_conflict_with_new_task():
    owner = create_owner()

    max_pet = owner.pets[0]
    max_pet.add_task(
        Task(
            description="Feed pet",
            time="08:00",
            frequency="daily",
            duration_minutes=30,
            priority="medium",
            category="feeding",
        )
    )

    engine = AIEngine(owner)

    response = engine.process_request(
        "Walk Max every morning at 8:15 AM for 30 minutes."
    )

    assert response.success is True
    assert response.task_created is True
    assert response.conflict_detected is True
    assert len(response.conflicts) == 1


def test_engine_ignores_unrelated_existing_conflict():
    owner = create_owner()

    max_pet = owner.pets[0]
    luna_pet = owner.pets[1]

    max_pet.add_task(
        Task(
            description="Feed pet",
            time="08:00",
            duration_minutes=30,
            category="feeding",
        )
    )

    luna_pet.add_task(
        Task(
            description="Groom pet",
            time="08:00",
            duration_minutes=30,
            category="grooming",
        )
    )

    engine = AIEngine(owner)

    response = engine.process_request(
        "Walk Max every morning at 10 AM for 30 minutes."
    )

    assert response.success is True
    assert response.task_created is True
    assert response.conflict_detected is False
    assert response.conflicts == []


def test_engine_logs_workflow_steps():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Feed Luna every day at 7 AM for 15 minutes."
    )

    assert response.logs
    assert response.logs[0] == "Received user request."
    assert "Request passed guardrail checks." in response.logs
    assert any("Parsed request" in log for log in response.logs)
    assert any("Created task" in log for log in response.logs)
    assert any("Retrieved" in log for log in response.logs)


def test_engine_retrieves_guidance_for_created_task():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Walk Max every morning at 8 AM for 30 minutes."
    )

    assert response.success is True
    assert response.knowledge_guidance is not None
    assert response.knowledge_guidance.category == "walk"
    assert response.knowledge_guidance.title == "Exercise Guidance"
    assert response.knowledge_guidance.confidence == 1.0


def test_engine_retrieves_medication_safety_guidance():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Give Luna her prescribed medication every day "
        "at 7 PM for 10 minutes."
    )

    assert response.success is True
    assert response.task_created is True
    assert response.knowledge_guidance is not None
    assert response.knowledge_guidance.category == "medication"
    assert "veterinarian" in response.knowledge_guidance.tip.lower()


def test_engine_logs_retrieval_step():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Feed Luna every day at 7 AM for 15 minutes."
    )

    assert response.success is True
    assert any("Retrieved" in log for log in response.logs)


def test_engine_blocks_unsafe_medication_request():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "How much medication should I give Max?"
    )

    assert response.success is False
    assert response.task_created is False
    assert "licensed veterinarian" in response.message.lower()
    assert any(
        "medication_dosage" in log
        for log in response.logs
    )


def test_engine_blocks_human_medication_request():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Schedule 200 mg of ibuprofen for Max at 8 PM."
    )

    assert response.success is False
    assert response.task_created is False
    assert "licensed veterinarian" in response.message.lower()
    assert any(
        "human_medication" in log
        for log in response.logs
    )


def test_engine_allows_prescribed_medication_schedule():
    owner = create_owner()
    engine = AIEngine(owner)

    response = engine.process_request(
        "Give Luna her prescribed medication every day "
        "at 7 PM for 10 minutes."
    )

    assert response.success is True
    assert response.task_created is True
    assert response.created_task is not None
    assert response.created_task.category == "medication"
    assert response.created_task.priority == "high"