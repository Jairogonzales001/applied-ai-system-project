# PawPal AI

## Overview

PawPal AI is an intelligent pet-care scheduling assistant built in Python and Streamlit.

This project extends my original CodePath PawPal+ project by adding an applied AI workflow that allows users to create pet-care tasks using natural language instead of manually entering every field.

The system can:

- Parse natural-language requests
- Create structured pet-care tasks
- Detect scheduling conflicts
- Retrieve pet-care guidance
- Apply responsible AI guardrails
- Explain its workflow through logs
- Evaluate reliability through automated testing

This project demonstrates practical AI engineering concepts including natural-language processing, modular system design, retrieval, responsible AI, testing, and user interface development.

---

# Features

- Natural language task creation
- Object-oriented scheduling system
- Daily and weekly recurring tasks
- Conflict detection
- Knowledge retrieval
- Medication safety guardrails
- Parser confidence scoring
- AI workflow logging
- Automated evaluation harness
- Streamlit interface
- Automated pytest testing

---

# AI Workflow

```
User Request
      │
      ▼
Guardrails
      │
      ▼
Natural Language Parser
      │
      ▼
Task Validation
      │
      ▼
Scheduler
      │
      ▼
Conflict Detection
      │
      ▼
Knowledge Retrieval
      │
      ▼
AI Response
```

---

# Project Structure

```
app.py
ai_engine.py
ai_task_parser.py
guardrails.py
knowledge_retriever.py
evaluate.py
pawpal_system.py

data/
    pet_care.json

diagrams/
    architecture.mmd

tests/

model_card.md
README.md
```

---

# Setup

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install streamlit pytest
```

---

# Running the Application

Start the Streamlit application.

```bash
python -m streamlit run app.py
```

---

# Example Requests

### Walking

```
Walk Max every morning at 8 AM for 30 minutes.
```

Expected result:

- Task created
- Exercise guidance retrieved
- Schedule updated

---

### Medication Reminder

```
Give Luna her prescribed medication every day at 7 PM for 10 minutes.
```

Expected result:

- Task created
- Medication Safety guidance displayed
- High-priority task added

---

### Unsafe Request

```
How much medication should I give Max?
```

Expected result:

- Request blocked
- No task created
- User advised to consult a licensed veterinarian

---

# Sample Output

```
Task successfully added for Max.

Exercise Guidance

Choose a walk duration and intensity that matches your
pet's age, health, breed, and activity level.

Current Schedule

08:00 - Max
Walk pet

AI Workflow

✓ Received request
✓ Passed guardrails
✓ Parsed request
✓ Created task
✓ Retrieved guidance
```

---

# Responsible AI

PawPal AI is designed to assist with scheduling and organization only.

The system intentionally does **not**:

- Diagnose illnesses
- Recommend treatments
- Calculate medication dosages
- Replace a licensed veterinarian

Instead, PawPal AI blocks unsafe requests through its guardrail system and encourages users to seek professional veterinary advice.

Examples of blocked requests include:

```
How much medication should I give my dog?
```

```
Can you diagnose my cat?
```

```
Should I give my dog ibuprofen?
```

---

# Knowledge Retrieval

PawPal AI retrieves guidance from a local JSON knowledge base.

Current categories include:

- Feeding
- Walking
- Grooming
- Medication Safety
- Veterinary Appointments
- General Pet Care

The retrieved guidance is intended to provide general educational information and should not replace advice from a licensed veterinarian.

---

# Evaluation

The project includes an evaluation harness (`evaluate.py`) that tests several common scenarios.

Current evaluation cases include:

- Daily walking request
- Medication scheduling
- Missing information
- Unknown pet
- Unsafe dosage request
- Human medication request

Run the evaluation:

```bash
python evaluate.py
```

---

# Automated Testing

Run the test suite.

```bash
python -m pytest -v
```

The project currently includes automated tests for:

- Scheduler logic
- AI Task Parser
- AI Engine
- Knowledge Retrieval
- Responsible AI Guardrails

Example output:

```
=========================== 29 passed in 0.05s ===========================
```

---

# Architecture

The application is divided into modular components.

| File | Purpose |
|------|---------|
| `app.py` | Streamlit user interface |
| `pawpal_system.py` | Core scheduling logic |
| `ai_task_parser.py` | Converts natural language into structured tasks |
| `ai_engine.py` | Coordinates the complete AI workflow |
| `knowledge_retriever.py` | Retrieves pet-care guidance |
| `guardrails.py` | Blocks unsafe medical requests |
| `evaluate.py` | Reliability evaluation harness |

The complete architecture diagram is located in:

```
diagrams/architecture.mmd
```

---

# Demo Walkthrough

1. Launch the Streamlit application.
2. Create an owner.
3. Add one or more pets.
4. Enter a natural-language request.
5. The AI engine validates the request.
6. Guardrails check for unsafe content.
7. The parser extracts task details.
8. The scheduler creates the task.
9. Conflicts are checked.
10. Relevant pet-care guidance is retrieved.
11. The updated schedule is displayed.
12. Workflow logs explain how the AI reached its decision.

---

# AI Engineering Concepts Demonstrated

This project demonstrates several applied AI engineering concepts:

- Natural Language Processing
- Rule-Based Information Extraction
- AI Workflow Orchestration
- Retrieval-Augmented Guidance
- Responsible AI Guardrails
- Reliability Testing
- Modular Software Design
- Object-Oriented Programming
- Streamlit Application Development
- Automated Testing with Pytest

---

# Future Improvements

Possible future enhancements include:

- Multiple task parsing in a single request
- More flexible language understanding
- Support for additional pet species
- Calendar integration
- Persistent database storage
- User authentication
- Expanded veterinary knowledge base
- Multilingual support
- AI-generated scheduling suggestions
- Mobile application support

---

# Author

**Jairo Gonzales**

CodePath AI110 Final Project

2026