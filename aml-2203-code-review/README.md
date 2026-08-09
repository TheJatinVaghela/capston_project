# AML-2203 — Code Review, Quality Assessment & Refactoring

**Course:** 2026S-AML-2203-OTT01 — Advanced Python AI & ML Tools  
**Group category:** Python-Groups  
**Codebase reviewed:** SupportFlow / AML-2404 Flask backend (`backend/*.py`)

## What’s in this folder

| Path | Purpose |
|------|---------|
| `AML-2203-Code-Review-Technical-Report.pdf` | **Main deliverable** — technical report |
| `before/update_knowledge_before.py` | Code excerpt **before** refactor |
| `after/update_knowledge_after.py` | Code excerpt **after** refactor |
| `analysis/` | flake8 / pylint / black outputs |
| `scripts/` | Helpers to snapshot code and regenerate the PDF |

## One improvement implemented

**Refactor:** remove duplicated knowledge **plan word-limit** checks and `business_info` seeding in `update_knowledge` (`backend/app.py`).

- Added `_knowledge_word_limit_response(...)`
- Added `_seed_knowledge_business_info(...)`
- Also cleaned `count_words` in `backend/config.py` (module-level `import re`)

## Reproduce analysis

From the repo root (with venv active):

```powershell
pip install pylint flake8 black reportlab
flake8 backend --max-line-length=100 --count --exit-zero
pylint backend/auth.py backend/config.py backend/security.py backend/language_util.py --exit-zero
black --check backend/auth.py backend/config.py backend/security.py backend/language_util.py
python aml-2203-code-review/scripts/generate_report_pdf.py
```

## Note

The PDF is the graded written deliverable. Improved source lives in the main `backend/` project; before/after excerpts here are for the report comparison.
