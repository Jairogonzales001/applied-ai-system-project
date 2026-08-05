from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


VALID_FREQUENCIES = {"one-time", "daily", "weekly"}
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_CATEGORIES = {
    "feeding",
    "walk",
    "medication",
    "appointment",
    "grooming",
    "other",
}


@dataclass
class Task:
    description: str
    time: str
    frequency: str = "one-time"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    duration_minutes: int = 30
    priority: str = "medium"
    category: str = "other"

    def __post_init__(self):
        """Validate and normalize task data after creation."""
        self.description = self.description.strip()
        self.frequency = self.frequency.lower().strip()
        self.priority = self.priority.lower().strip()
        self.category = self.category.lower().strip()

        if not self.description:
            raise ValueError("Task description cannot be empty.")

        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Frequency must be one of: {', '.join(sorted(VALID_FREQUENCIES))}."
            )

        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}."
            )

        if self.category not in VALID_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(sorted(VALID_CATEGORIES))}."
            )

        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than zero.")

        self._parse_time()

    def _parse_time(self) -> datetime:
        """Convert the stored time string into a datetime value."""
        try:
            parsed_time = datetime.strptime(self.time.strip(), "%H:%M").time()
        except ValueError as exc:
            raise ValueError("Time must use 24-hour HH:MM format.") from exc

        return datetime.combine(self.due_date, parsed_time)

    @property
    def start_datetime(self) -> datetime:
        """Return the task's starting date and time."""
        return self._parse_time()

    @property
    def end_datetime(self) -> datetime:
        """Return the task's ending date and time."""
        return self.start_datetime + timedelta(minutes=self.duration_minutes)

    def overlaps_with(self, other_task: "Task") -> bool:
        """Return True when two tasks overlap on the same date."""
        if self.due_date != other_task.due_date:
            return False

        return (
            self.start_datetime < other_task.end_datetime
            and other_task.start_datetime < self.end_datetime
        )

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create the next task if this task repeats daily or weekly."""
        if self.frequency == "daily":
            next_due_date = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due_date = self.due_date + timedelta(days=7)
        else:
            return None

        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            due_date=next_due_date,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
        )


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        self.name = self.name.strip()
        self.species = self.species.strip()

        if not self.name:
            raise ValueError("Pet name cannot be empty.")

        if not self.species:
            raise ValueError("Pet species cannot be empty.")

    def add_task(self, task: Task):
        """Add a task to this pet."""
        if not isinstance(task, Task):
            raise TypeError("Only Task objects can be added to a pet.")

        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self):
        self.name = self.name.strip()

        if not self.name:
            raise ValueError("Owner name cannot be empty.")

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        if not isinstance(pet, Pet):
            raise TypeError("Only Pet objects can be added to an owner.")

        self.pets.append(pet)

    def get_all_tasks(self):
        """Get all tasks for all pets."""
        all_tasks = []

        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet.name, task))

        return all_tasks


class Scheduler:
    PRIORITY_ORDER = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    def __init__(self, owner: Owner):
        """Create a scheduler for an owner."""
        if not isinstance(owner, Owner):
            raise TypeError("Scheduler requires an Owner object.")

        self.owner = owner

    def sort_by_time(self):
        """Sort all tasks by date, time, and priority."""
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda item: (
                item[1].due_date,
                item[1].start_datetime,
                self.PRIORITY_ORDER[item[1].priority],
            ),
        )

    def filter_by_pet(self, pet_name):
        """Return tasks for one pet."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if pet.lower() == pet_name.lower()
        ]

    def filter_by_status(self, completed):
        """Return tasks by completion status."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.completed == completed
        ]

    def mark_task_complete(self, pet_name, task_description):
        """Complete a task and create its next occurrence when recurring."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                for task in pet.tasks:
                    if (
                        task.description.lower() == task_description.lower()
                        and not task.completed
                    ):
                        task.mark_complete()

                        next_task = task.create_next_occurrence()
                        if next_task:
                            pet.add_task(next_task)

                        return True

        return False

    def detect_conflicts(self):
        """Detect overlapping tasks occurring on the same date."""
        conflicts = []
        all_tasks = self.owner.get_all_tasks()

        for current_index, (pet_name, task) in enumerate(all_tasks):
            for other_pet_name, other_task in all_tasks[current_index + 1 :]:
                if task.overlaps_with(other_task):
                    conflicts.append(
                        {
                            "pet_1": pet_name,
                            "task_1": task.description,
                            "pet_2": other_pet_name,
                            "task_2": other_task.description,
                            "date": task.due_date.isoformat(),
                            "start_1": task.time,
                            "end_1": task.end_datetime.strftime("%H:%M"),
                            "start_2": other_task.time,
                            "end_2": other_task.end_datetime.strftime("%H:%M"),
                            "recommended_priority": self._higher_priority_task(
                                pet_name,
                                task,
                                other_pet_name,
                                other_task,
                            ),
                        }
                    )

        return conflicts

    def _higher_priority_task(
        self,
        pet_name: str,
        task: Task,
        other_pet_name: str,
        other_task: Task,
    ) -> str:
        """Explain which conflicting task should receive priority."""
        task_rank = self.PRIORITY_ORDER[task.priority]
        other_rank = self.PRIORITY_ORDER[other_task.priority]

        if task_rank < other_rank:
            return f"Keep {pet_name}'s '{task.description}' because it has higher priority."

        if other_rank < task_rank:
            return (
                f"Keep {other_pet_name}'s '{other_task.description}' "
                "because it has higher priority."
            )

        return "Both tasks have the same priority and require owner review."