PawPal AI

Overview

PawPal AI is an intelligent pet-care scheduling assistant built in Python and Streamlit.

This project extends my original CodePath Module 2 project, PawPal+.

The original PawPal+ application focused on object-oriented programming to help pet owners manage recurring care tasks, generate daily schedules, and detect scheduling conflicts. This final project expands those capabilities into a complete applied AI system by adding natural-language task parsing, AI workflow orchestration, knowledge retrieval, responsible AI guardrails, and reliability evaluation.

The system can:

Parse natural-language requests

Create structured pet-care tasks

Detect scheduling conflicts

Retrieve pet-care guidance

Apply responsible AI guardrails

Explain its workflow through logs

Evaluate reliability through automated testing

This project demonstrates practical AI engineering concepts including natural-language processing, modular system design, retrieval, responsible AI, testing, and user interface development.

Features

Natural language task creation

Object-oriented scheduling system

Daily and weekly recurring tasks

Conflict detection

Knowledge retrieval

Medication safety guardrails

Parser confidence scoring

AI workflow logging

Automated evaluation harness

Streamlit interface

Automated pytest testing

AI Workflow

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

Project Structure

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

Setup

python -m venv .venv

Activate the environment.

macOS/Linux:

source .venv/bin/activate

Windows:

.venv\Scripts\activate

Install dependencies:

pip install streamlit pytest

Running the Application

python -m streamlit run app.py

Sample Interactions

Example 1 – Walking Request

Input

Walk Max every morning at 8 AM for 30 minutes.

Output

Task successfully added for Max.

Exercise Guidance

Choose a walk duration and intensity that matches your pet's age, health, breed, and activity level.

AI Workflow
✓ Passed guardrails
✓ Parsed request
✓ Created task
✓ Retrieved guidance

Example 2 – Medication Reminder

Input

Give Luna her prescribed medication every day at 7 PM for 10 minutes.

Output

Task successfully added for Luna.

Medication Safety

Always follow your veterinarian's prescribed schedule.

AI Workflow
✓ Passed guardrails
✓ Parsed request
✓ Created task
✓ Retrieved guidance

Example 3 – Unsafe Request

Input

How much medication should I give Max?

Output

PawPal can schedule care tasks, but it cannot provide medication dosages, diagnoses, or treatment recommendations.

Please contact a licensed veterinarian.

AI Workflow
✓ Guardrail blocked request

Design Decisions

I designed PawPal AI using a modular architecture so each component has a single responsibility.

ai_task_parser.py converts natural-language requests into structured tasks.

ai_engine.py coordinates the AI workflow.

pawpal_system.py manages scheduling and conflict detection.

knowledge_retriever.py retrieves pet-care guidance.

guardrails.py blocks unsafe requests.

evaluate.py measures reliability.

I chose rule-based parsing instead of a large language model because it produces deterministic behavior, requires no API keys, and is easier to test and debug. The trade-off is that it is less flexible when users enter unexpected wording.

Responsible AI

PawPal AI is a scheduling assistant only.

It intentionally does not:

Diagnose illnesses

Recommend treatments

Calculate medication dosages

Replace a licensed veterinarian

Unsafe requests are blocked and users are directed to consult a licensed veterinarian.

Knowledge Retrieval

The application retrieves guidance from a local JSON knowledge base (data/pet_care.json) covering:

Feeding

Walking

Grooming

Medication Safety

Veterinary Appointments

General Pet Care

Evaluation

Run the evaluation harness:

python evaluate.py

It evaluates:

Daily walking request

Medication scheduling

Missing information

Unknown pet

Unsafe dosage request

Human medication request

Automated Testing

Run:

python -m pytest -v

The project includes automated tests for:

Scheduler

AI Task Parser

AI Engine

Knowledge Retrieval

Responsible AI Guardrails

Example:

=========================== 29 passed in 0.05s ===========================

Architecture

File

Purpose

app.py

Streamlit interface

pawpal_system.py

Scheduling logic

ai_task_parser.py

Natural-language parsing

ai_engine.py

AI orchestration

knowledge_retriever.py

Knowledge retrieval

guardrails.py

Safety guardrails

evaluate.py

Reliability evaluation

Architecture diagram:

diagrams/architecture.mmd

Demo Walkthrough

Launch the Streamlit application.

Create an owner.

Add one or more pets.

Enter a natural-language request.

Review the parsed task.

Review retrieved guidance.

Review workflow logs.

View the updated schedule.

Reflection

Building PawPal AI taught me that creating an AI application involves much more than generating responses. Reliable AI requires validation, testing, safety guardrails, modular architecture, and clear documentation.

This project reinforced the importance of testing successful and unsuccessful inputs and showed me how multiple AI components can work together to build a trustworthy application.

Future Improvements

Multiple-task parsing

Calendar integration

Persistent storage

Expanded veterinary knowledge base

Multilingual support

Mobile application

Author

Jairo Gonzales

CodePath AI110 Final Project

2026