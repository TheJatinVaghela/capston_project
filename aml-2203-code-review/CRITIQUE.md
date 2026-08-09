# Written Critique (supporting notes)

These notes feed Section 5 of the PDF technical report.

## Logic clarity & correctness
- Chat preparation is already shared via `_prepare_chat_request` — good pattern.
- Knowledge update duplicated the plan word-limit rule (fixed).
- Billing handlers are correct but dense; harder to reason about failure modes.

## PEP 8 / style
- flake8: long lines dominate; minor blank-line and unused-global issues.
- black: not fully applied across all modules.
- Naming is generally clear (`require_business_owner`, `sanitize_chat_message`).

## Modularity
- Strength: `security.py`, `auth.py`, `config.plan_limits`.
- Weakness: business rules still sometimes live inside Flask views.
- Opportunity: shared time helper; Stripe sync helpers.

## Unnecessary complexity
- `OllamaAIChatbot` is large (many responsibilities: retrieval, prompts, sanitize, streaming).
- Acceptable for a capstone MVP; would split in a longer maintenance phase.
