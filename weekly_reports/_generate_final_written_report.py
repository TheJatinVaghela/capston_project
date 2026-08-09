"""
Generate AML-2404 Final Written Report from FinalWrittenReport-Template structure,
using weekly progress reports as the primary source of truth.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "FinalWrittenReport.docx"
TEMPLATE = ROOT / "FinalWrittenReport-Template.docx"


def set_run_font(run, size=11, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def add_para(doc, text, *, size=11, bold=False, italic=False, align="left", space_after=8):
    p = doc.add_paragraph()
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        set_run_font(run, size=14 if level == 1 else 12, bold=True)
    return h


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(item, style="List Bullet")
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        for run in p.runs:
            set_run_font(run, size=11)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            for run in p.runs:
                set_run_font(run, size=10, bold=True)
    for r_i, row in enumerate(rows, start=1):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i].cells[c_i]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    set_run_font(run, size=10)
    doc.add_paragraph()
    return table


def build():
    # Start from a clean document that mirrors the template sections
    # (template placeholders are instructional; we produce the filled academic report).
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # ── Cover Page ──────────────────────────────────────────────────────────
    add_para(doc, "Lambton College", size=14, bold=True, align="center", space_after=4)
    add_para(
        doc,
        "School of Computer Studies / AI and ML Lab",
        size=12,
        align="center",
        space_after=4,
    )
    add_para(doc, "Course: AML-2404 – AI and ML Lab", size=12, align="center", space_after=18)
    add_para(
        doc,
        "AI-Powered Customer Service Chatbot Using Python, NLTK and AI Model Integration",
        size=16,
        bold=True,
        align="center",
        space_after=6,
    )
    add_para(
        doc,
        "(SupportFlow Multi-Tenant SaaS Evolution)",
        size=12,
        italic=True,
        align="center",
        space_after=18,
    )
    add_para(doc, "Final Written Report", size=14, bold=True, align="center", space_after=18)
    add_para(doc, "Group Name:", size=11, bold=True, align="center", space_after=4)
    add_para(
        doc,
        "Dev Pankajkumar Bajaniya, Jatin Vaghela, Pratikkumar Bhupendrabhai Chavda, "
        "Amal Satheesan, Karop Dezosa Sebastian",
        size=11,
        align="center",
        space_after=12,
    )
    add_para(doc, "Group Members:", size=11, bold=True, align="center", space_after=6)

    members = [
        ("Dev", "Pankajkumar Bajaniya", ""),
        ("Jatin", "Vaghela", ""),
        ("Pratikkumar", "Bhupendrabhai Chavda", ""),
        ("Amal", "Satheesan", ""),
        ("Karop Dezosa", "Sebastian", ""),
    ]
    add_table(
        doc,
        ["First name", "Last Name", "Student number"],
        members,
    )
    add_para(
        doc,
        "Faculty Supervisor: William Pourmajidi",
        size=11,
        align="center",
        space_after=4,
    )
    add_para(
        doc,
        f"Submission date: {date(2026, 8, 7).strftime('%B %d, %Y')}",
        size=11,
        align="center",
        space_after=4,
    )
    add_para(
        doc,
        "Primary sources: Weekly Progress Reports (Weeks 1–12), Minutes of Meeting (Weeks 10–11), "
        "and project proposal materials.",
        size=10,
        italic=True,
        align="center",
        space_after=24,
    )
    doc.add_page_break()

    # ── Table of Contents ───────────────────────────────────────────────────
    add_heading_custom(doc, "Table of Contents", level=1)
    toc_items = [
        "1. Abstract",
        "2. Introduction",
        "3. Methods",
        "    3.1 Context and Setting of the Study",
        "    3.2 Study Design",
        "    3.3 Data Set Details",
        "    3.4 Main Study Variables",
        "    3.5 Data Collection Instruments and Procedures",
        "    3.6 Analysis Methods",
        "4. Results",
        "5. Discussion",
        "6. Conclusions and Future Work",
        "7. References",
        "8. Acknowledgment",
        "9. Appendices",
        "    Appendix A. Week-by-Week Progress Summary",
        "    Appendix B. System Architecture Overview",
        "    Appendix C. Subscription Plan Limits",
        "    Appendix D. Testing Summary",
    ]
    for item in toc_items:
        add_para(doc, item, size=11, space_after=2)
    add_para(doc, "List of Tables", size=12, bold=True, space_after=4)
    for item in [
        "Table 1. Team Roles and Responsibilities",
        "Table 2. Hybrid Response Pipeline Tiers",
        "Table 3. Subscription Plan Feature Limits",
        "Table 4. Representative Evaluation Outcomes by Capability",
        "Table 5. Twelve-Week Progress Timeline (Appendix A)",
    ]:
        add_para(doc, item, size=11, space_after=2)
    add_para(doc, "List of Figures", size=12, bold=True, space_after=4)
    for item in [
        "Figure 1. High-level SupportFlow system architecture (described in Appendix B)",
        "Figure 2. Chat request processing flow (signup → knowledge → chat → billing → embed)",
    ]:
        add_para(doc, item, size=11, space_after=2)
    doc.add_page_break()

    # ── Abstract ────────────────────────────────────────────────────────────
    add_heading_custom(doc, "1. Abstract", level=1)
    add_para(
        doc,
        "This final written report synthesizes the twelve-week AML-2404 capstone project that "
        "developed an AI-powered customer service chatbot and later evolved it into SupportFlow, "
        "a multi-tenant SaaS platform. Organizations struggle with delayed support, repetitive "
        "inquiries, and limited after-hours coverage. The team addressed these problems by building "
        "a Python/Flask backend, React frontend, SQLite multi-tenant data layer, NLTK-based intent "
        "and FAQ handling, and local Ollama large-language-model (LLM) generation with retrieval-"
        "augmented knowledge. Over the semester the system progressed from a rule-based chatbot "
        "prototype to a product with JWT authentication, free-text knowledge bases, streaming chat, "
        "multilingual replies, Stripe test-mode subscriptions (Basic, Professional, Premium), "
        "plan-based limits, an embeddable website widget, and a laptop-hosted public demo via "
        "secure tunnels. Weekly progress reports (Weeks 1–12) document iterative design, failures "
        "(for example incomplete AI metadata logging, language drift, CORS/signup issues, and "
        "tunnel SPA routing bugs), and corrective actions. Final regression demos confirmed an "
        "end-to-end path from signup through knowledge editing, AI chat, billing, and embed chat "
        "history. The report discusses evaluation quality, including overfitting/underfitting "
        "risks for both pattern matching and local LLMs, and outlines future work such as managed "
        "cloud hosting and stronger automated testing.",
        align="justify",
    )

    # ── Introduction ────────────────────────────────────────────────────────
    add_heading_custom(doc, "2. Introduction", level=1)
    add_para(
        doc,
        "Customer support organizations frequently face delayed responses, repetitive questions, "
        "high operational cost, and weak 24/7 availability. Human agents spend substantial time "
        "answering similar shipping, return, account, and product questions, which reduces capacity "
        "for complex cases and harms customer satisfaction. Traditional FAQ pages and static "
        "scripts help only when customers can find the right page and when wording matches exactly. "
        "The AML-2404 project set out to design and implement an intelligent chatbot that can "
        "automate routine support conversations while remaining controllable, explainable enough "
        "for academic demonstration, and extensible toward a real multi-business product.",
        align="justify",
    )
    add_para(
        doc,
        "The original project proposal framed a twelve-week sprint covering research and planning, "
        "UI/UX design, database development, chatbot implementation, NLP integration, testing, "
        "deployment, and documentation/presentation. Weekly progress reports show how the team "
        "executed that plan while adapting scope: early weeks established a hybrid FAQ → pattern "
        "matching → Ollama pipeline; mid-sprint weeks integrated AI metadata logging, payments, "
        "and debugging; later weeks delivered SaaS features (multi-tenant businesses, Stripe plans, "
        "RAG-style knowledge, multilingual support, embed widget history) and closed with testing, "
        "laptop deployment, presentation practice, and final polish (Weeks 10–12).",
        align="justify",
    )
    add_para(
        doc,
        "The final system, branded SupportFlow in later weeks, allows a business owner to register, "
        "create one or more businesses (subject to plan limits), paste free-text knowledge, preview "
        "the chatbot, subscribe via Stripe test mode, customize Premium chat colors, and embed a "
        "widget on an external website. AI answers are generated with local Ollama models "
        "(for example Mistral, Llama3, Neural-Chat) constrained by support-only guardrails and "
        "language locking so replies match the customer’s current message language. This report "
        "uses the weekly reports as primary evidence to explain what was built, how it was "
        "evaluated, what failed, and what remains for future work.",
        align="justify",
    )

    add_heading_custom(doc, "2.1 Team and Roles", level=2)
    add_para(
        doc,
        "Table 1 summarizes the stable role assignments reported across weekly progress reports. "
        "Team leadership rotated by week for collaboration assessment.",
        align="justify",
    )
    add_table(
        doc,
        ["Member", "Primary role", "Representative contributions (from weekly reports)"],
        [
            [
                "Dev Pankajkumar Bajaniya",
                "Backend Developer",
                "Flask APIs, chat/streaming, Stripe, SPA hosting, CORS/tunnel config, auth hardening",
            ],
            [
                "Jatin Vaghela",
                "AI / ML Specialist",
                "NLTK intents, prompts, multilingual locking, social vs KB routing, model comparison",
            ],
            [
                "Pratikkumar B. Chavda",
                "Database Manager",
                "Conversation logging, AI metadata, plan/schema fields, session history, integrity checks",
            ],
            [
                "Amal Satheesan",
                "Frontend / UI Designer",
                "React UI, billing cards, history sidebar, Premium colors, embed UX, presentation visuals",
            ],
            [
                "Karop Dezosa Sebastian",
                "Documentation & Deployment (early weeks)",
                "Report coordination, presentation rehearsal support, documentation packaging",
            ],
        ],
    )

    add_heading_custom(doc, "2.2 Problem Statement and Objectives", level=2)
    add_bullets(
        doc,
        [
            "Reduce delayed responses to repetitive customer questions using automated NLP/AI replies.",
            "Provide a maintainable hybrid pipeline combining FAQs, patterns, and generative AI.",
            "Log conversations and model usage for analysis and demonstration.",
            "Evolve toward a multi-tenant SaaS with authentication, billing, and website embedding.",
            "Validate quality through weekly testing, smoke/API checks, and final regression demos.",
            "Document deployment suitable for faculty demonstration (including laptop tunnel hosting).",
        ],
    )

    # ── Methods ─────────────────────────────────────────────────────────────
    add_heading_custom(doc, "3. Methods", level=1)
    add_para(
        doc,
        "This section describes the technical methods used across the twelve-week sprint. "
        "It includes approaches that succeeded and approaches that initially failed or were "
        "partially complete, as recorded in weekly reports. Code screenshots are avoided; "
        "instead the methods are explained through architecture, design choices, data, and "
        "evaluation procedures.",
        align="justify",
    )

    add_heading_custom(doc, "3.1 Context and Setting of the Study", level=2)
    add_para(
        doc,
        "The study was conducted as an academic capstone at Lambton College under AML-2404 "
        "(AI and ML Lab), supervised by Professor William Pourmajidi. Development occurred in "
        "a local engineering environment: Python 3 with Flask on the backend, React (Vite/MUI) "
        "on the frontend, SQLite for persistence in the matured SaaS phase, and Ollama running "
        "local LLMs on team laptops. Stripe was used only in test mode. Later weeks added "
        "Cloudflare/ngrok tunnels so the laptop could host a temporary public demo URL while "
        "keeping the database and AI model on-device (Week 11–12 reports; HOSTING_LAPTOP guidance).",
        align="justify",
    )

    add_heading_custom(doc, "3.2 Study Design", level=2)
    add_para(
        doc,
        "The project followed an iterative build–measure–learn design aligned to the twelve-week "
        "Gantt plan (research/planning → UI → database → chatbot/NLP → AI integration → "
        "testing/debugging → deployment → documentation/presentation). Each week produced a "
        "progress report with individual and team contributions, challenges, deliverables, and "
        "next-week tasks. This created a longitudinal design: earlier weeks validated a hybrid "
        "chatbot for a single demo business (TechFlow-style FAQ/product data), while later weeks "
        "re-architected toward multi-tenant SupportFlow SaaS capabilities.",
        align="justify",
    )
    add_para(
        doc,
        "Technically, the chatbot uses a tiered decision design (Table 2). High-confidence FAQ "
        "or pattern matches return deterministic answers; otherwise the system retrieves relevant "
        "knowledge snippets and calls Ollama. Failures such as model timeouts fall back to safe "
        "support messages. SaaS design adds JWT-protected owner APIs, widget-key public embed "
        "APIs, and subscription gates for preview limits versus paid embed use.",
        align="justify",
    )
    add_table(
        doc,
        ["Tier", "Method", "Purpose", "Typical latency (reported/demo experience)"],
        [
            ["1", "FAQ / knowledge match", "Exact or high-similarity support answers", "Near-instant"],
            ["2", "NLTK / pattern intents", "Greeting and structured intent routing", "Fast"],
            ["3", "Ollama LLM + RAG context", "Open-ended support answers from business knowledge", "1–3+ seconds"],
        ],
    )

    add_heading_custom(doc, "3.3 Data Set Details", level=2)
    add_para(
        doc,
        "The project did not rely on a single public ML benchmark dataset. Instead it used "
        "curated domain data and live conversational logs:",
        align="justify",
    )
    add_bullets(
        doc,
        [
            "Business knowledge files / free-text knowledge bases describing company policies, products, and FAQs (initially structured JSON; later free-text with plan word limits).",
            "intents.json patterns for greetings and support categories used in early hybrid routing.",
            "SQLite tables for users, businesses, sessions, messages, subscription/plan fields, and widget keys (mature SaaS schema).",
            "Operational chat logs generated during weekly testing (intent distribution, model_used, confidence, timestamps).",
            "Stripe test checkout/webhook events for subscription status and plan assignment (Basic / Professional / Premium).",
            "Multilingual probe utterances (English plus romanized Gujarati/Hindi and other markers) for language-lock evaluation (Week 9).",
        ],
    )

    add_heading_custom(doc, "3.4 Main Study Variables", level=2)
    add_para(
        doc,
        "Independent / configurable variables included AI model choice (Mistral, Llama3, Neural-Chat), "
        "use_ai flags, knowledge text content and word count, subscription plan and status, "
        "preview chat count, allowed embed origins, and chat color theme (Premium). Dependent "
        "outcomes included response correctness/relevance, intent or routing label, model_used, "
        "latency/user-perceived speed, language match to the current user message, whether "
        "guardrails blocked non-support topics, and whether plan limits correctly blocked "
        "over-quota knowledge or extra businesses. Process variables tracked across weeks included "
        "completion percentage estimates, open defects, and collaboration ratings.",
        align="justify",
    )

    add_heading_custom(doc, "3.5 Data Collection Instruments and Procedures", level=2)
    add_para(
        doc,
        "Instruments and procedures evolved with the product:",
        align="justify",
    )
    add_bullets(
        doc,
        [
            "Manual conversational test scripts covering FAQs, ambiguous queries, edge cases (empty/long input), and multi-turn follow-ups (Weeks 5–8).",
            "Intent category pass/fail checks against intents.json patterns (early weeks; later partially superseded by RAG/AI-first routing).",
            "API smoke testing of /chat, /chat/stream, /auth, /businesses, /billing, /sessions, and embed endpoints (Week 10 plan and Week 11 execution notes).",
            "UI walkthroughs for signup/login, knowledge editor word counters, billing cards, history sidebar, and widget history/new-chat (Weeks 9–12).",
            "Stripe CLI webhook forwarding and checkout confirmation flows in test mode.",
            "Public-tunnel checks ensuring the SPA (not JSON status) loads at “/” and that same-origin API calls succeed (Week 11).",
            "Presentation practice and demo-video rehearsals documented in Week 10–11 MOM and Week 12 final report.",
        ],
    )
    add_para(
        doc,
        "Approaches that did not fully work (recorded as challenges): incomplete AI metadata "
        "logging on fallback/timeout paths (Week 7–8); language drift when earlier turns used "
        "another language (Week 9); greeting phrases incorrectly answered from knowledge "
        "(Week 9); multiple Flask processes causing stale CORS during signup (Week 9); "
        "legacy unit tests expecting old intent tags while the live system became RAG/AI-first "
        "(Week 10/11); tunnel homepage returning JSON until Accept/SPA routing was fixed "
        "(Week 11). Each failure informed a corrective design change rather than being ignored.",
        align="justify",
    )

    add_heading_custom(doc, "3.6 Analysis Methods", level=2)
    add_para(
        doc,
        "Analysis combined qualitative review and quantitative operational metrics. Qualitatively, "
        "the AI specialist and team rated reply clarity, tone, and support relevance during "
        "prompt-optimization cycles. Quantitatively, analytics views and logs summarized intent "
        "or route distribution, FAQ vs pattern vs Ollama usage, and fallback rates (Week 5 "
        "analytics dashboard notes; later SaaS stats endpoints). Plan-limit analysis checked "
        "word counts against configured maxima. For generative models, the team discussed "
        "generalization risk: overly narrow patterns underfit diverse phrasings; overly long "
        "or unconstrained LLM prompts can overfit demo scripts or leak training-style phrasing "
        "(for example “Based on the provided reference data”), which was mitigated with "
        "sanitizers and stricter prompts (Week 9). Final analysis in Week 12 was an end-to-end "
        "regression demo: signup → knowledge → chat → billing → embed widget.",
        align="justify",
    )

    # ── Results ─────────────────────────────────────────────────────────────
    add_heading_custom(doc, "4. Results", level=1)
    add_para(
        doc,
        "Results are organized by capability, reflecting cumulative weekly deliverables rather "
        "than a single offline accuracy score. Where classical ML metrics (precision/recall) "
        "were not the primary artifact, operational success criteria from weekly reports are used.",
        align="justify",
    )

    add_heading_custom(doc, "4.1 Hybrid Chatbot and AI Integration Results", level=2)
    add_para(
        doc,
        "By mid-sprint the team delivered a working hybrid chatbot: NLTK/pattern intents, FAQ "
        "responses, Flask APIs, React chat UI, and conversation logging (Week 6). Week 7–8 "
        "integrated Ollama AI responses with UI indicators and improved metadata logging after "
        "initial incomplete tracking on failures. Week 5 (earlier milestone packaging) reported "
        "end-to-end verification across intent categories, multi-turn context (last 2–3 messages), "
        "and analytics for model usage. Later SaaS weeks shifted primary answering toward "
        "RAG-style knowledge retrieval with streaming tokens (SSE) for better UX (Week 9).",
        align="justify",
    )

    add_heading_custom(doc, "4.2 Multilingual and Guardrail Results", level=2)
    add_para(
        doc,
        "Week 9 reports show successful automatic language matching for major customer languages, "
        "including romanized Gujarati/Hindi greetings, after fixing language drift and removing "
        "source-disclosure phrasing. A knowledge-free social path prevented short hellos from "
        "being answered with company facts. Support-only guardrails reduced off-topic generative "
        "answers during demos.",
        align="justify",
    )

    add_heading_custom(doc, "4.3 SaaS, Billing, and Embed Results", level=2)
    add_para(
        doc,
        "The matured product supports multi-tenant businesses with JWT auth, free-text knowledge "
        "editing, Stripe test subscriptions, and an embeddable widget with history/new-chat "
        "resume (Weeks 8–9). Table 3 lists plan limits enforced in backend and reflected in UI.",
        align="justify",
    )
    add_table(
        doc,
        ["Plan", "Price (CAD/mo, test catalog)", "Max businesses", "Knowledge words", "Chat colors"],
        [
            ["Free", "0", "1", "200", "No"],
            ["Basic", "5", "1", "500", "No"],
            ["Professional", "10", "5", "2000", "No"],
            ["Premium", "20", "10", "5000", "Yes"],
        ],
    )

    add_heading_custom(doc, "4.4 Testing, Deployment, and Final Readiness", level=2)
    add_para(
        doc,
        "Week 10 focused on unit/smoke/API testing, bug fixes, and frontend updates (planned in "
        "Week 9; progress reflected in Week 11 narrative and MOM). Week 11 completed remaining "
        "debugging and a laptop deployment prototype: Flask serves the built React SPA; "
        "PUBLIC_BASE_URL / tunnel CORS enable sharing; Stripe redirects use the public URL. "
        "Week 12 completed final documentation, presentation/video preparation, presentation "
        "practice, final polish, and closing regression demos. Table 4 summarizes representative "
        "outcomes.",
        align="justify",
    )
    add_table(
        doc,
        ["Capability", "Evaluation focus", "Reported outcome"],
        [
            ["Auth & tenancy", "Signup/login, owner isolation", "Fixed CORS/port issues; JWT flows demo-ready"],
            ["Knowledge limits", "Word caps by plan", "Enforced in API; UI counters added"],
            ["Chat quality", "Relevance, language, greetings", "Improved after Week 9 prompt/sanitizer fixes"],
            ["Billing", "Checkout/portal/webhook/confirm", "Test-mode plans activate; limits apply"],
            ["Embed widget", "Key auth, history, origins", "History/new chat; subscription gating"],
            ["Public demo host", "Tunnel SPA + Ollama on laptop", "Achieved after SPA “/” fix; URL refresh needed"],
            ["Legacy unit tests", "Old intent expectations", "Many mismatches vs RAG/AI-first design"],
        ],
    )

    add_heading_custom(doc, "4.5 Overfitting and Underfitting Discussion", level=2)
    add_para(
        doc,
        "Although the system is not a classical supervised classifier trained on a large labeled "
        "corpus, overfitting and underfitting still apply:",
        align="justify",
    )
    add_para(
        doc,
        "Underfitting. Early rule-based patterns failed on paraphrases and multi-intent utterances "
        "(Week 6 challenges). If patterns or FAQs are too sparse, the bot underfits real customer "
        "language and over-relies on the LLM. Multilingual underfitting appeared when romanized "
        "greetings were absent from detectors.",
        align="justify",
    )
    add_para(
        doc,
        "Overfitting. Intent patterns tuned only to demo scripts can overfit a small phrase set "
        "and look accurate in rehearsal while failing on novel wording. LLM prompts that dump "
        "excessive knowledge or conversation history can overfit local context, producing brittle "
        "or overly verbose answers and sometimes disclosing “reference data” style phrasing "
        "(addressed in Week 9). Streaming generation with adaptive context/predict sizes was "
        "used to balance quality and latency without memorizing a single demo transcript.",
        align="justify",
    )
    add_para(
        doc,
        "Mitigations included expanding patterns where needed, preferring retrieved knowledge "
        "snippets over full dumps for short messages, language locking to the current turn, "
        "social routing for greetings, reply sanitization, and human smoke tests beyond the "
        "original FAQ list. Remaining risk: local LLMs can still drift; continuous evaluation "
        "with fresh utterances is required before production.",
        align="justify",
    )

    # ── Discussion ──────────────────────────────────────────────────────────
    add_heading_custom(doc, "5. Discussion", level=1)
    add_para(
        doc,
        "The weekly reports show a clear thesis: a hybrid NLP + local LLM chatbot can automate "
        "routine support, and the same core can be productized into a multi-tenant SaaS with "
        "billing and embedding. The most important scientific/engineering insight is that "
        "generative quality depends as much on routing, retrieval, and sanitization as on the "
        "base model. Failures were informative: incomplete logging taught the team to treat "
        "fallback paths as first-class; language drift taught strict per-message language "
        "control; SaaS bugs around CORS and SPA hosting taught that deployment configuration "
        "is part of model-serving success when demos leave localhost.",
        align="justify",
    )
    add_para(
        doc,
        "Scope management also mattered. Features such as voice input, file upload, dark mode, "
        "Docker/cloud production hosting, and sentiment analysis were deprioritized (Weeks 4–5 "
        "and Week 9 notes) so the team could finish billing limits, multilingual quality, embed "
        "history, testing, and demonstration packaging. This trade-off improved deliverability "
        "within twelve weeks while leaving a documented future backlog.",
        align="justify",
    )
    add_para(
        doc,
        "From an academic evaluation perspective, the project’s evidence base is strongest in "
        "process documentation and end-to-end operational testing, and weaker in large-scale "
        "offline ML benchmarks. That is appropriate for a systems capstone that ships a working "
        "assistant, but it implies caution when generalizing accuracy claims. The legacy "
        "intent unit tests’ poor match to the final RAG/AI-first behavior illustrates how "
        "evaluation assets must evolve with architecture.",
        align="justify",
    )

    # ── Conclusions ─────────────────────────────────────────────────────────
    add_heading_custom(doc, "6. Conclusions and Future Work", level=1)
    add_para(
        doc,
        "Across twelve weeks the team designed, implemented, tested, and demonstrated an "
        "AI-powered customer service chatbot that evolved into SupportFlow: a multi-tenant "
        "platform with knowledge-grounded local AI, multilingual replies, Stripe test billing, "
        "plan limits, and an embeddable widget. Weekly progress reports document continuous "
        "integration of backend, AI, database, and frontend work, including failures and "
        "repairs. The final Week 12 report closed documentation, presentation practice, "
        "demo-video preparation, and regression polish. The system addresses real-world delayed "
        "and repetitive support by providing instant, knowledge-aware answers under owner "
        "control, suitable for academic demonstration and controlled sharing via laptop hosting.",
        align="justify",
    )
    add_para(
        doc,
        "Future work remaining beyond the graded sprint includes: (1) managed cloud deployment "
        "of API/database with a hosted model API for 24/7 uptime; (2) expanded automated tests "
        "aligned to RAG/AI-first routing and billing helpers; (3) production hardening "
        "(HTTPS termination, strict webhooks, backups, monitoring); (4) optional voice/file "
        "features deferred earlier; and (5) broader multilingual evaluation sets. These items "
        "extend the research activity without blocking the completed twelve-week deliverable.",
        align="justify",
    )

    # ── References ──────────────────────────────────────────────────────────
    add_heading_custom(doc, "7. References", level=1)
    refs = [
        "Bird, S., Klein, E., & Loper, E. (2009). Natural language processing with Python. O’Reilly Media. (NLTK)",
        "Flask development team. (n.d.). Flask documentation. https://flask.palletsprojects.com/",
        "Meta / Ollama community. (n.d.). Ollama documentation (local LLM runtime). https://ollama.com/",
        "Stripe, Inc. (n.d.). Stripe API and Checkout documentation (test mode). https://stripe.com/docs",
        "React / Meta Open Source. (n.d.). React documentation. https://react.dev/",
        "Team weekly progress reports, AML-2404, Lambton College (Weeks 1–12, 2026).",
        "Team minutes of meeting, AML-2404 (Week 10 and Week 11 MOM documents, 2026).",
        "Project proposal PDF: AI-Powered Customer Service Chatbot Using Python and NLTK "
        "(Professional Academic Project Proposal – 12-Week Development Sprint).",
        "American Psychological Association. (2020). Publication manual of the American Psychological "
        "Association (7th ed.). (formatting guidance)",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        for run in p.runs:
            set_run_font(run, size=11)

    # ── Acknowledgment ──────────────────────────────────────────────────────
    add_heading_custom(doc, "8. Acknowledgment", level=1)
    add_para(
        doc,
        "The authors thank Professor William Pourmajidi for supervision and feedback throughout "
        "the AML-2404 capstone. We acknowledge each team member’s weekly contributions recorded "
        "in the progress reports: backend engineering (Dev), AI/ML design and evaluation (Jatin), "
        "database and analytics integrity (Pratik), frontend/UX and presentation materials (Amal), "
        "and documentation/deployment coordination (Dezosa in earlier weeks). We also acknowledge "
        "open-source communities behind Python, Flask, NLTK, React, and Ollama, and Stripe’s test "
        "platform for enabling safe billing demonstrations.",
        align="justify",
    )

    # ── Appendices ──────────────────────────────────────────────────────────
    doc.add_page_break()
    add_heading_custom(doc, "9. Appendices", level=1)

    add_heading_custom(doc, "Appendix A. Week-by-Week Progress Summary", level=2)
    add_para(
        doc,
        "Table 5 consolidates the weekly progress reports used as sources for this final written report.",
        align="justify",
    )
    add_table(
        doc,
        ["Week", "Focus (from weekly reports)", "Key outcomes"],
        [
            ["1–2", "Planning / kickoff (proposal & early progress decks)", "Problem framing, roles, 12-week plan alignment"],
            ["3–4", "Foundational progress (PDF weekly reports)", "Early architecture, UI/database foundations, scope decisions"],
            ["5", "UI polish, multi-turn context, analytics, presentation prep", "Demo packaging milestone; multi-turn Ollama context"],
            ["6", "Rule-based chatbot core", "Intents, FAQ flow, Flask/React/DB prototype (~55% note)"],
            ["7", "AI integration", "Ollama in pipeline; UI AI indicators; partial AI metadata logging"],
            ["8", "Debug, payments, model improvements", "Logging fixes, payment workflow updates, E2E testing"],
            ["9", "Advanced SaaS features", "History, multilingual, RAG/stream, Stripe plans/limits, embed history"],
            ["10", "Testing & frontend updates (plan + MOM)", "Unit/smoke/API testing focus; presentation video discussion"],
            ["11", "Deployment + remaining debugging", "Laptop tunnel SPA host; CORS/public URL; demo sharing"],
            ["12", "Final docs, presentation, polish (final weekly report)", "Closing regression, video/practice, submission readiness"],
        ],
    )

    add_heading_custom(doc, "Appendix B. System Architecture Overview (Figure 1 description)", level=2)
    add_para(
        doc,
        "Figure 1 (conceptual). Client layers: React dashboard (owners) and embeddable widget "
        "(end customers). Both call the Flask API. Auth uses JWT for owners and widget keys for "
        "public embed. The chatbot module performs FAQ/pattern routing and RAG-informed Ollama "
        "generation. SQLite stores tenants, knowledge, sessions/messages, and subscription fields. "
        "Stripe test mode updates plan/status via checkout confirmation and webhooks. For shared "
        "demos, Cloudflare/ngrok tunnels terminate HTTPS to the laptop-hosted Flask process, which "
        "serves both API and built frontend assets.",
        align="justify",
    )
    add_para(
        doc,
        "Figure 2 (conceptual). Owner journey: register/login → create business → paste knowledge "
        "(word-limit check) → preview chat (streaming) → choose plan on Billing → embed widget.js "
        "with data-key on an external site → customers chat with history resume.",
        align="justify",
    )

    add_heading_custom(doc, "Appendix C. Subscription Plan Limits", level=2)
    add_para(
        doc,
        "See Table 3 in Results. Account-level business limits use the highest active plan across "
        "a user’s businesses; knowledge word limits and Premium colors apply per business plan "
        "status (active/trialing).",
        align="justify",
    )

    add_heading_custom(doc, "Appendix D. Testing Summary", level=2)
    add_bullets(
        doc,
        [
            "Functional/smoke: auth, knowledge save, preview chat, billing checkout, embed chat/history.",
            "API: chat, streaming, sessions, businesses, settings, billing confirm/sync/webhook.",
            "AI quality: multilingual probes, greeting vs KB routing, sanitizer checks, model switch checks.",
            "Deployment: SPA build served by Flask; tunnel URL loads UI; Stripe redirect URLs use public base.",
            "Known gap: legacy intent unit suite not fully aligned to RAG/AI-first routing (documented in Weeks 10–11).",
        ],
    )

    add_para(
        doc,
        "— End of Final Written Report —",
        size=11,
        italic=True,
        align="center",
        space_after=6,
    )

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
