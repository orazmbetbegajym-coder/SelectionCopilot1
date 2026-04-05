# Selection Copilot

## Problem
Traditional university screening often over-relies on GPA and polished applications.
As a result, admissions teams may miss high-potential candidates with strong growth trajectories,
community impact, teamwork, or leadership signals that are not fully visible through grades alone.

## Solution
Selection Copilot is an explainable AI-assisted admissions support system.
It helps universities review applicants holistically by analyzing:

- GPA
- essay quality and specificity
- achievements
- extracurricular activities
- long-term commitment
- leadership signals
- teamwork readiness
- contribution potential
- AI-writing risk indicators

The system does not replace the admissions committee.
It provides structured decision support for:

- Advance
- Review
- Hold

---

## 🔥 Behavioral Intelligence Layer (NEW)

We integrate an additional behavioral signal using Jungian archetype analysis.

If candidate essays do not fully reflect potential, the system evaluates:

- personality archetypes (Hero, Creator, Leader, etc.)
- motivation patterns
- behavioral traits

This allows:

- detecting hidden potential
- identifying non-obvious high performers
- reducing bias from purely text-based evaluation

---

## Core Value
Selection Copilot helps universities:

- find hidden potential
- reduce over-reliance on GPA-only filtering
- compare applicants more fairly
- support human reviewers with explainable analysis
- identify high-impact contributors for campus life

---

## Architecture
The system is built as a modular FastAPI application.

### Main modules
- `app.py` — web application, routes, uploads, shortlist, validation
- `scoring/analyzer.py` — feature extraction, scoring engine
- `scoring/advisor.py` — recommendation logic and insights
- `scoring/ranker.py` — candidate ranking and scoring fusion
- `scoring/data_store.py` — in-memory candidate storage
- `archetype.py` — behavioral analysis layer (NEW)
- `templates/` — user interface

---

## Pipeline
Input → Feature Extraction → Scoring Engine → Baseline Comparison → Behavioral Layer → Advice Layer → Reviewer Decision Flow

### Input
- form input or CSV upload
- GPA
- essay
- achievements
- activities
- contribution fields
- programs participated
- long-term activities
- evidence files
- archetype (optional)

---

### Feature Extraction
The model extracts signals such as:
- leadership potential
- growth trajectory
- motivation
- community orientation
- teamwork readiness
- authenticity
- evidence strength

---

### Behavioral Layer (NEW)
The system adds an additional signal:

- Jungian archetype analysis
- behavioral pattern detection
- hidden potential scoring

---

### Scoring Engine
Final score is calculated using a hybrid model:

- Essay & achievements → 70%
- Behavioral (archetype) signal → 30%

---

### Baseline Comparison
The model compares itself with:
- Baseline A: GPA only
- Baseline B: GPA + achievements

---

### Validation Layer
The project includes a validation dataset:
- expected label
- expected hidden potential
- baseline accuracy
- model accuracy
- top error cases

---

### Advice Layer
The system generates:
- recommendation
- strengths
- weaknesses with reasons
- improvement plan
- candidate profile type
- university value
- behavioral risks

---

### Reviewer Decision Flow
Human reviewers make the final choice:
- Advance
- Review
- Hold

---

## Fairness
The model does **not** use sensitive attributes such as:
- gender
- ethnicity
- religion
- family income
- political views
- medical data

The system uses only academic, behavioral, and contribution-oriented signals.

---

## Why this is better than baseline
GPA-only systems often miss:
- hidden potential
- students with strong growth but weaker polish
- community builders
- team contributors
- future campus leaders

Selection Copilot improves decision support by using:
- behavioral signals
- archetype-based analysis
- explainable outputs

---

## Validation
The project includes:
- baseline comparison
- validation dataset
- error analysis
- hidden potential detection
- AI-writing risk analysis

---

## Example Use Case
A university admissions committee wants to reduce false negatives in selection.

A student with medium GPA but strong leadership, community work, and growth trajectory
might be rejected by a GPA-only system.

Selection Copilot can surface that candidate using:
- behavioral signals
- archetype analysis
- explainable scoring

---

## Run
```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload