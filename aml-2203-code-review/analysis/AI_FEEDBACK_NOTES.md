# AI-assisted review notes (Cursor)

Date: Aug 2026  
Codebase: SupportFlow Flask backend (AML-2404 semester project)

## Prompt themes used
1. “Where is duplicated business logic in backend/app.py?”
2. “Which pylint findings are worth fixing vs noise for a student report?”
3. “Propose one low-risk, high-clarity refactor with clear before/after.”

## AI suggestions considered
| Suggestion | Decision |
|------------|----------|
| Extract duplicated knowledge word-limit JSON | **Accepted & implemented** |
| Extract shared `now_utc` module | Deferred (good follow-up) |
| Split Stripe webhook into helpers | Deferred (larger change, higher risk) |
| Mass-add docstrings everywhere | Deferred (cosmetic for this submission) |
| Auto-format entire repo with black | Deferred (out of scope for one improvement) |

## Why the chosen refactor
- Touches a real product rule (plan knowledge limits)
- Removes copy-paste error payloads that could drift
- Easy to explain in a before/after PDF
- Does not change external API contracts when within/over limits
