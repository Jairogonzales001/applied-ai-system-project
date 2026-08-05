# PawPal AI Model Card

## System Overview

PawPal AI is an intelligent pet-care scheduling assistant that extends my original Module 2 PawPal+ project. The original project used Python object-oriented programming to represent owners, pets, and care tasks. It also supported recurring tasks, task sorting, completion tracking, and basic schedule-conflict detection.

The updated system allows users to describe a pet-care task in natural language. PawPal AI parses the request, validates required information, creates a structured task, checks the schedule for conflicts, retrieves relevant pet-care guidance, applies safety guardrails, and records its workflow decisions.

## Intended Use

PawPal AI is intended to help pet owners organize routine care activities such as:

- Feeding
- Walks
- Grooming
- Prescribed medication reminders
- Veterinary appointments

The application is designed as a scheduling and planning assistant. It is not intended to diagnose illnesses, recommend treatments, prescribe medication, or calculate medication dosages.

## System Components

The system contains the following major components:

- **Natural-language task parser:** Converts a written request into structured task information.
- **AI engine:** Coordinates parsing, validation, task creation, conflict detection, retrieval, and response generation.
- **PawPal scheduler:** Sorts tasks, creates recurring tasks, and detects overlapping schedules.
- **Knowledge retriever:** Retrieves category-specific pet-care guidance from a local JSON knowledge base.
- **Guardrails:** Blocks requests for medication dosages, medical diagnoses, treatment recommendations, and unsafe human medication use.
- **Evaluation harness:** Runs predefined test cases and reports pass/fail results and a reliability score.
- **Streamlit interface:** Allows users to add pets, submit natural-language requests, and review schedules and AI workflow logs.

## Data and Knowledge Sources

The system uses a small local knowledge base stored in:

```text
data/pet_care.json