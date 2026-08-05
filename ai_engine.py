from dataclasses import dataclass, field
from typing import Optional

from ai_task_parser import ParsedTask, parse_task_request
from guardrails import Guardrails
from knowledge_retriever import KnowledgeRetriever, RetrievedGuidance
from pawpal_system import Owner, Scheduler, Task


@dataclass
class AIResponse:
    """Result returned by the PawPal AI workflow."""

    success: bool
    message: str
    task_created: bool = False
    conflict_detected: bool = False
    pet_name: Optional[str] = None
    parsed_task: Optional[ParsedTask] = None
    created_task: Optional[Task] = None
    conflicts: list[dict] = field(default_factory=list)
    knowledge_guidance: Optional[RetrievedGuidance] = None
    logs: list[str] = field(default_factory=list)


class AIEngine:
    """Coordinates safety checks, parsing, task creation, retrieval, and conflicts."""

    def __init__(self, owner: Owner):
        if not isinstance(owner, Owner):
            raise TypeError("AIEngine requires an Owner object.")

        self.owner = owner
        self.scheduler = Scheduler(owner)
        self.retriever = KnowledgeRetriever()
        self.guardrails = Guardrails()

    def process_request(self, user_input: str) -> AIResponse:
        """Process one natural-language task request from start to finish."""

        logs = ["Received user request."]

        guardrail_result = self.guardrails.check(user_input)

        if not guardrail_result.allowed:
            logs.append(
                "Guardrail blocked request: "
                + ", ".join(guardrail_result.matched_rules)
            )

            return AIResponse(
                success=False,
                message=guardrail_result.message,
                logs=logs,
            )

        logs.append("Request passed guardrail checks.")

        try:
            parsed = parse_task_request(
                user_input,
                known_pets=[pet.name for pet in self.owner.pets],
            )
        except ValueError as exc:
            logs.append("Parser rejected the request.")

            return AIResponse(
                success=False,
                message=str(exc),
                logs=logs,
            )

        logs.append(
            f"Parsed request with confidence {parsed.confidence:.2f}."
        )

        if not parsed.is_complete:
            missing = ", ".join(parsed.missing_fields)
            logs.append(f"Missing required information: {missing}.")

            return AIResponse(
                success=False,
                message=f"I need more information: {missing}.",
                parsed_task=parsed,
                logs=logs,
            )

        selected_pet = self._find_pet(parsed.pet_name)

        if selected_pet is None:
            logs.append(f"Pet '{parsed.pet_name}' was not found.")

            return AIResponse(
                success=False,
                message=f"I could not find a pet named '{parsed.pet_name}'.",
                pet_name=parsed.pet_name,
                parsed_task=parsed,
                logs=logs,
            )

        try:
            task = parsed.to_task()
        except ValueError as exc:
            logs.append("Task validation failed.")

            return AIResponse(
                success=False,
                message=str(exc),
                pet_name=selected_pet.name,
                parsed_task=parsed,
                logs=logs,
            )

        selected_pet.add_task(task)
        logs.append(f"Created task for {selected_pet.name}.")

        all_conflicts = self.scheduler.detect_conflicts()

        relevant_conflicts = self._find_relevant_conflicts(
            selected_pet.name,
            task,
            all_conflicts,
        )

        if relevant_conflicts:
            logs.append(
                f"Detected {len(relevant_conflicts)} conflict(s) "
                "involving the new task."
            )

            message = (
                f"Task added for {selected_pet.name}, "
                "but a scheduling conflict was detected."
            )
        else:
            logs.append("No conflicts detected for the new task.")
            message = f"Task successfully added for {selected_pet.name}."

        try:
            guidance = self.retriever.retrieve(
                category=parsed.category,
                query=user_input,
            )

            logs.append(
                f"Retrieved '{guidance.title}' with confidence "
                f"{guidance.confidence:.2f}."
            )
        except (FileNotFoundError, ValueError, KeyError) as exc:
            logs.append(f"Knowledge retrieval failed: {exc}")
            guidance = None

        return AIResponse(
            success=True,
            message=message,
            task_created=True,
            conflict_detected=bool(relevant_conflicts),
            pet_name=selected_pet.name,
            parsed_task=parsed,
            created_task=task,
            conflicts=relevant_conflicts,
            knowledge_guidance=guidance,
            logs=logs,
        )

    def _find_pet(self, pet_name: str):
        """Return the matching pet without requiring exact capitalization."""

        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return pet

        return None

    @staticmethod
    def _find_relevant_conflicts(
        pet_name: str,
        task: Task,
        conflicts: list[dict],
    ) -> list[dict]:
        """Return only conflicts involving the newly created task."""

        relevant = []

        for conflict in conflicts:
            first_matches = (
                conflict["pet_1"].lower() == pet_name.lower()
                and conflict["task_1"].lower() == task.description.lower()
                and conflict["start_1"] == task.time
            )

            second_matches = (
                conflict["pet_2"].lower() == pet_name.lower()
                and conflict["task_2"].lower() == task.description.lower()
                and conflict["start_2"] == task.time
            )

            if first_matches or second_matches:
                relevant.append(conflict)

        return relevant