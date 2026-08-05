import streamlit as st

from ai_engine import AIEngine
from pawpal_system import Owner, Pet, Scheduler


st.set_page_config(
    page_title="PawPal AI",
    page_icon="🐾",
    layout="centered",
)

st.title("🐾 PawPal AI")
st.write(
    "An intelligent pet-care scheduling assistant with natural-language "
    "task creation, conflict detection, retrieval, and safety guardrails."
)


if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")


def find_pet(pet_name: str):
    """Return a matching pet from session state."""
    for pet in st.session_state.owner.pets:
        if pet.name.lower() == pet_name.lower():
            return pet

    return None


st.subheader("Owner Information")

owner_name = st.text_input(
    "Owner name",
    value=st.session_state.owner.name,
)

if st.button("Save owner"):
    cleaned_name = owner_name.strip()

    if cleaned_name:
        st.session_state.owner.name = cleaned_name
        st.success("Owner saved.")
    else:
        st.warning("Please enter an owner name.")


st.divider()

st.subheader("Add a Pet")

pet_name = st.text_input("Pet name")
species = st.selectbox("Species", ["Dog", "Cat", "Other"])

if st.button("Add pet"):
    cleaned_pet_name = pet_name.strip()

    if not cleaned_pet_name:
        st.warning("Please enter a pet name.")
    elif find_pet(cleaned_pet_name):
        st.warning("A pet with that name already exists.")
    else:
        st.session_state.owner.add_pet(
            Pet(cleaned_pet_name, species)
        )
        st.success(f"{cleaned_pet_name} was added.")


if st.session_state.owner.pets:
    pet_rows = [
        {
            "Name": pet.name,
            "Species": pet.species,
            "Tasks": len(pet.tasks),
        }
        for pet in st.session_state.owner.pets
    ]

    st.write("Current pets")
    st.table(pet_rows)
else:
    st.info("Add at least one pet before creating tasks.")


st.divider()

st.subheader("AI Task Assistant")

st.write(
    "Describe one pet-care task in natural language. Include the pet name "
    "and time so PawPal can create the task reliably."
)

st.caption(
    "Example: Walk Max every morning at 8 AM for 30 minutes."
)

user_request = st.text_area(
    "Pet-care request",
    placeholder=(
        "Give Luna her prescribed medication every day "
        "at 7 PM for 10 minutes."
    ),
    height=110,
)

if st.button("Process request", type="primary"):
    if not st.session_state.owner.pets:
        st.warning("Add a pet before submitting a task request.")
    else:
        engine = AIEngine(st.session_state.owner)
        response = engine.process_request(user_request)

        if response.success:
            st.success(response.message)
        else:
            st.error(response.message)

        if response.parsed_task is not None:
            parsed = response.parsed_task

            st.subheader("Parsed Request")

            parsed_rows = [
                {
                    "Pet": parsed.pet_name or "Missing",
                    "Description": parsed.description,
                    "Time": parsed.time or "Missing",
                    "Frequency": parsed.frequency,
                    "Duration": f"{parsed.duration_minutes} minutes",
                    "Priority": parsed.priority.title(),
                    "Category": parsed.category.title(),
                    "Confidence": f"{parsed.confidence:.2f}",
                }
            ]

            st.table(parsed_rows)

        if response.conflict_detected:
            st.subheader("Conflict Warning")

            for conflict in response.conflicts:
                st.error(
                    f"{conflict['pet_1']}'s "
                    f"'{conflict['task_1']}' "
                    f"({conflict['start_1']}–{conflict['end_1']}) "
                    f"overlaps with "
                    f"{conflict['pet_2']}'s "
                    f"'{conflict['task_2']}' "
                    f"({conflict['start_2']}–{conflict['end_2']})."
                )

                st.info(conflict["recommended_priority"])

        if response.knowledge_guidance is not None:
            guidance = response.knowledge_guidance

            st.subheader(guidance.title)
            st.write(guidance.tip)
            st.caption(
                f"Source: {guidance.source} · "
                f"Retrieval confidence: {guidance.confidence:.2f}"
            )

        with st.expander("AI workflow log"):
            for log_entry in response.logs:
                st.write(f"- {log_entry}")


st.divider()

st.subheader("Current Schedule")

scheduler = Scheduler(st.session_state.owner)
tasks = scheduler.sort_by_time()

if tasks:
    schedule_rows = []

    for scheduled_pet_name, task in tasks:
        schedule_rows.append(
            {
                "Date": task.due_date.isoformat(),
                "Start": task.time,
                "End": task.end_datetime.strftime("%H:%M"),
                "Pet": scheduled_pet_name,
                "Task": task.description,
                "Category": task.category.title(),
                "Priority": task.priority.title(),
                "Frequency": task.frequency,
                "Completed": task.completed,
            }
        )

    st.table(schedule_rows)
else:
    st.info("No tasks have been created yet.")


if st.button("Reset application"):
    st.session_state.owner = Owner("Jordan")
    st.rerun()