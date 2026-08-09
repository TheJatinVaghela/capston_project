"""
Generate AML-2203 Final Term Project PDF technical report.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "AML-2203-Code-Review-Technical-Report.pdf"
BEFORE = (ROOT / "before" / "update_knowledge_before.py").read_text(encoding="utf-8")
AFTER = (ROOT / "after" / "update_knowledge_after.py").read_text(encoding="utf-8")


def styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontSize=16,
            leading=20,
            spaceAfter=8,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontSize=13,
            leading=16,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#0b1f33"),
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#123047"),
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["BodyText"],
            fontSize=10,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "BulletCustom",
            parent=base["BodyText"],
            fontSize=10,
            leading=13,
            leftIndent=14,
            spaceAfter=3,
        ),
        "meta": ParagraphStyle(
            "MetaCustom",
            parent=base["Normal"],
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "CodeCustom",
            parent=base["Code"],
            fontName="Courier",
            fontSize=6.5,
            leading=8,
            leftIndent=0,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "CaptionCustom",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#444444"),
            spaceAfter=8,
            alignment=TA_LEFT,
        ),
    }
    return styles


def p(text, style):
    return Paragraph(text.replace("\n", "<br/>"), style)


def code_block(text, style, max_chars=5500):
    clipped = text if len(text) <= max_chars else text[:max_chars] + "\n# ... truncated ..."
    return Preformatted(clipped, style)


def build():
    s = styles()
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="AML-2203 Code Review, Quality Assessment & Refactoring",
        author="Group 2026S-AML-2203-OTT01",
    )
    story = []

    story.append(p("2026S-AML-2203-OTT01 — Advanced Python AI &amp; ML Tools", s["meta"]))
    story.append(
        p(
            "Final Term Project — Code Review, Quality Assessment &amp; Refactoring",
            s["title"],
        )
    )
    story.append(p("Technical Report (PDF Deliverable)", s["meta"]))
    story.append(Spacer(1, 8))

    meta = [
        ["Course", "AML-2203 Advanced Python AI & ML Tools"],
        ["Group", "2026S-AML-2203-OTT01-Advanced Python AI & ML - 2"],
        ["Category", "Python-Groups"],
        [
            "Codebase",
            "SupportFlow / AML-2404 AI Customer Service Chatbot (Python Flask backend)",
        ],
        ["Primary modules reviewed", "backend/app.py, chatbot.py, database.py, config.py, auth.py, security.py, language_util.py"],
        ["Static analysis tools", "pylint 4.0.6, flake8, black 26.5.1"],
        ["AI assistant used", "Cursor / Copilot-style AI for review suggestions and refactor design"],
    ]
    t = Table(meta, colWidths=[1.6 * inch, 5.0 * inch])
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t)

    # 1. Introduction
    story.append(p("1. Introduction &amp; Project Objective", s["h1"]))
    story.append(
        p(
            "This report critically evaluates and improves the quality of our semester Python "
            "codebase developed for the AML-2404 / SupportFlow customer-service chatbot SaaS. "
            "The backend is a multi-module Flask application with JWT auth, SQLite persistence, "
            "Stripe billing, RAG-style knowledge retrieval, and local Ollama AI integration. "
            "The goal of AML-2203 is not to rebuild the product, but to practice clean-code "
            "habits: PEP 8 compliance, modularity, readable control flow, static analysis, "
            "and one meaningful refactor grounded in evidence from tools and manual review.",
            s["body"],
        )
    )

    # 2. Codebase selection
    story.append(p("2. Selected Codebase", s["h1"]))
    story.append(
        p(
            "We selected the <b>SupportFlow Flask backend</b> because it contains substantial "
            "logic (auth decorators, multi-tenant database helpers, billing webhooks, chat "
            "orchestration, and a large OllamaAIChatbot class). This provides enough surface "
            "area for a meaningful review of naming, duplication, complexity, and PEP issues.",
            s["body"],
        )
    )
    story.append(p("• <b>app.py</b> — HTTP routes, CORS/security hooks, billing, chat endpoints", s["bullet"]))
    story.append(p("• <b>chatbot.py</b> — intent/RAG/AI response generation and sanitization", s["bullet"]))
    story.append(p("• <b>database.py</b> — SQLite schema, sessions, plan-aware public views", s["bullet"]))
    story.append(p("• <b>config.py / auth.py / security.py / language_util.py</b> — supporting modules", s["bullet"]))

    # 3. Method
    story.append(p("3. Review Method (Manual + Tools + AI)", s["h1"]))
    story.append(p("3.1 Manual review", s["h2"]))
    story.append(
        p(
            "We read module boundaries and high-traffic paths (auth, knowledge update, chat "
            "prepare/stream, billing sync). We looked for duplicated business rules, unclear "
            "names, oversized functions, broad exception handlers, and places where plan limits "
            "or timestamps were redefined instead of shared.",
            s["body"],
        )
    )
    story.append(p("3.2 Static analysis tools", s["h2"]))
    story.append(
        p(
            "We ran <b>flake8</b> (style / unused names), <b>pylint</b> (complexity, docs, "
            "imports), and <b>black --check</b> (formatter drift). Reports are stored under "
            "<font face='Courier'>aml-2203-code-review/analysis/</font>.",
            s["body"],
        )
    )
    story.append(p("3.3 AI-assisted feedback", s["h2"]))
    story.append(
        p(
            "Cursor AI was used to: (1) summarize hotspots in large files, (2) propose "
            "candidate refactors with lowest product risk, and (3) draft helper signatures "
            "that preserve API behavior. AI suggestions were treated as hypotheses and "
            "validated against the live route logic before changing code.",
            s["body"],
        )
    )

    # 4. Tool findings
    story.append(p("4. Summary of Tool Findings", s["h1"]))
    findings = [
        ["Tool", "Key observations"],
        [
            "flake8",
            "17 issues across reviewed files: mostly E501 long lines; also E305 blank-line "
            "spacing in config.py, unused global in chatbot cache helper (F824), trailing "
            "blank line (W391), and one E203 slice spacing style conflict with black.",
        ],
        [
            "pylint (core modules)",
            "Rated about 9.08/10 on auth/config/security/language_util. Common notes: missing "
            "docstrings (C0116), import-outside-toplevel (C0415) for lazy imports, "
            "broad-exception-caught (W0718), too-many-return-statements in language detect.",
        ],
        [
            "pylint (app + database)",
            "Rated about 8.99/10. Hotspots: too-many-branches / statements on billing webhook "
            "and sync handlers; many broad Exception catches; logging-fstring-interpolation; "
            "missing docstrings on several Flask views.",
        ],
        [
            "black --check",
            "Would reformat language_util.py and config.py — formatting is mostly consistent "
            "but not fully black-normalized across every module.",
        ],
    ]
    ft = Table(findings, colWidths=[1.3 * inch, 5.3 * inch])
    ft.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b1f33")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(ft)

    # 5. Critique
    story.append(p("5. Written Critique — Key Observations", s["h1"]))
    story.append(p("5.1 Strengths", s["h2"]))
    story.append(
        p(
            "The backend already shows good modular intent: auth decorators are isolated, "
            "security helpers centralize sanitization/rate limits, config owns plan limits, "
            "and chat endpoints share <font face='Courier'>_prepare_chat_request</font>. "
            "That shared chat preparation is an example of prior successful abstraction.",
            s["body"],
        )
    )
    story.append(p("5.2 Issues found (manual + tools)", s["h2"]))
    story.append(
        p(
            "1. <b>Duplicated business rules in <font face='Courier'>update_knowledge</font></b> — "
            "the plan word-limit error JSON and business_info defaults were copy-pasted in "
            "free-text and legacy structured branches. This risks inconsistent error messages "
            "and makes limit changes error-prone (DRY / modularity issue).",
            s["body"],
        )
    )
    story.append(
        p(
            "2. <b>Oversized route handlers</b> — Stripe confirm/sync/webhook functions exceed "
            "pylint branch/statement budgets. Flow is correct but hard to test in isolation.",
            s["body"],
        )
    )
    story.append(
        p(
            "3. <b>PEP / style drift</b> — long lines (E501), occasional missing blank lines "
            "(E305), and black drift in a few modules. Not runtime bugs, but reduce polish.",
            s["body"],
        )
    )
    story.append(
        p(
            "4. <b>Broad exception handling</b> — many <font face='Courier'>except Exception</font> "
            "blocks hide root causes; acceptable at HTTP edges, weaker inside helpers.",
            s["body"],
        )
    )
    story.append(
        p(
            "5. <b>Duplicate utilities</b> — <font face='Courier'>now_utc()</font> exists in both "
            "app.py and database.py; <font face='Courier'>count_words</font> previously imported "
            "<font face='Courier'>re</font> inside the function (fixed during cleanup).",
            s["body"],
        )
    )
    story.append(
        p(
            "6. <b>Documentation debt</b> — pylint C0116 on many small helpers; public helpers "
            "would benefit from one-line docstrings for newcomers.",
            s["body"],
        )
    )
    story.append(p("5.3 Suggested improvements (prioritized)", s["h2"]))
    story.append(p("• Extract duplicated knowledge limit / seeding helpers (implemented).", s["bullet"]))
    story.append(p("• Split Stripe webhook/sync into pure helpers + thin Flask views.", s["bullet"]))
    story.append(p("• Share a single time utility module for UTC timestamps.", s["bullet"]))
    story.append(p("• Narrow exception types near Stripe/API boundaries; keep generic catch only at top-level views.", s["bullet"]))
    story.append(p("• Run black + flake8 in CI to prevent style regressions.", s["bullet"]))
    story.append(p("• Add focused unit tests for plan word limits and auth decorators.", s["bullet"]))

    # 6. Implemented refactor
    story.append(PageBreak())
    story.append(p("6. Implemented Improvement — One Meaningful Refactor", s["h1"]))
    story.append(
        p(
            "We chose to refactor <b>knowledge plan-limit enforcement</b> in "
            "<font face='Courier'>backend/app.py</font>. This is a real business rule used by "
            "paying customers’ knowledge bases. Duplication here is more dangerous than a "
            "cosmetic rename because inconsistent limits could allow over-quota saves on one "
            "code path and reject them on another.",
            s["body"],
        )
    )
    story.append(p("6.1 What changed and why", s["h2"]))
    story.append(
        p(
            "We introduced two helpers: "
            "<font face='Courier'>_knowledge_word_limit_response(...)</font> centralizes counting "
            "and the 403 JSON payload; "
            "<font face='Courier'>_seed_knowledge_business_info(...)</font> centralizes default "
            "business_info fields. Both free-text and legacy structured update paths now call "
            "the same helpers. Behavior stays the same for valid/invalid payloads, but future "
            "copy or limit changes happen once. We also moved "
            "<font face='Courier'>import re</font> to module scope in config.py for "
            "<font face='Courier'>count_words</font> (PEP import style).",
            s["body"],
        )
    )
    story.append(p("6.2 Before (duplicated logic)", s["h2"]))
    story.append(code_block(BEFORE, s["code"], max_chars=4200))
    story.append(
        p(
            "Figure 1. Before — identical word-limit error blocks appear twice in update_knowledge.",
            s["caption"],
        )
    )
    story.append(p("6.3 After (shared helpers)", s["h2"]))
    story.append(code_block(AFTER, s["code"], max_chars=5200))
    story.append(
        p(
            "Figure 2. After — helpers own the rule; route focuses on request shape and persistence.",
            s["caption"],
        )
    )

    # 7. AI feedback section
    story.append(p("7. AI Tool Feedback Used", s["h1"]))
    story.append(
        p(
            "AI review suggested several candidates: extract now_utc, split webhook handlers, "
            "and remove knowledge-limit duplication. We accepted the knowledge-limit refactor "
            "because it scored highest on: (a) clear before/after teaching value, (b) low risk "
            "to runtime behavior, and (c) direct improvement to modularity of a business rule. "
            "AI-generated helper names were edited for clarity and type of return value "
            "(word_count, optional Flask error tuple).",
            s["body"],
        )
    )

    # 8. Reflection
    story.append(p("8. Final Reflection — What We Learned", s["h1"]))
    story.append(
        p(
            "Working on a real semester product made PEP and modularity issues more concrete "
            "than toy examples. Static tools quickly highlighted complexity and style debt, but "
            "manual review was still required to decide which findings matter for maintainability. "
            "Duplication of business rules is more costly than long lines: two identical error "
            "payloads can silently diverge. AI tools accelerate discovery and drafting, yet "
            "humans must verify that abstractions preserve API contracts. Going forward we would "
            "enforce formatter/linter checks earlier and extract helpers as soon as a rule appears "
            "a second time (Rule of Three / immediate DRY for critical limits).",
            s["body"],
        )
    )

    # 9. Deliverable index
    story.append(p("9. Folder Contents (Submission Package)", s["h1"]))
    story.append(p("• <font face='Courier'>AML-2203-Code-Review-Technical-Report.pdf</font> — this report", s["bullet"]))
    story.append(p("• <font face='Courier'>before/update_knowledge_before.py</font> — original excerpt", s["bullet"]))
    story.append(p("• <font face='Courier'>after/update_knowledge_after.py</font> — refactored excerpt", s["bullet"]))
    story.append(p("• <font face='Courier'>analysis/</font> — flake8, pylint, and black outputs", s["bullet"]))
    story.append(p("• <font face='Courier'>README.md</font> — how to reproduce the analysis", s["bullet"]))
    story.append(
        p(
            "The live improved code also exists in the main repository at "
            "<font face='Courier'>backend/app.py</font> and <font face='Courier'>backend/config.py</font>.",
            s["body"],
        )
    )

    story.append(Spacer(1, 12))
    story.append(
        p(
            "— End of Report — Group 2026S-AML-2203-OTT01 / SupportFlow Capstone Codebase —",
            s["meta"],
        )
    )

    doc.build(story)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
