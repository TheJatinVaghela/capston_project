"""Generate slide-by-slide speaking script for Final Presentation (4 members)."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor

OUT = r"D:\customer-service-chatbot\weekly_reports\Final-Presentation-Speaking-Script.docx"

SLIDES = [
    # Jatin 1-4
    {
        "num": 1,
        "title": "Title — SupportFlow",
        "speaker": "Jatin Vaghela",
        "screenshot": None,
        "script": (
            "Hello everyone. My name is Jatin Vaghela, and with my teammates Dev Bajaniya, "
            "Pratik Chavda, and Amal Satheesan, we present SupportFlow — our AML-2404 AI and ML Lab "
            "final project. SupportFlow is an AI-powered customer service chatbot that evolved into "
            "a multi-tenant SaaS platform. Our supervisor is Professor William Pourmajidi. "
            "In this presentation each of us will cover our area, and we will end with the product demo path and Q&A."
        ),
    },
    {
        "num": 2,
        "title": "Agenda",
        "speaker": "Jatin Vaghela",
        "screenshot": None,
        "script": (
            "Here is our agenda. I will start with the problem and objectives. Dev will explain the "
            "solution architecture, backend APIs, and billing. Pratik will cover the multi-tenant data "
            "model, logging, testing, and demo deployment. Amal will walk through the dashboard UI, "
            "knowledge editor, preview chat, and embed widget, then close with the demo path and future work. "
            "Please note: screenshots on later slides should show the live app pages labeled in the placeholders."
        ),
    },
    {
        "num": 3,
        "title": "The Problem",
        "speaker": "Jatin Vaghela",
        "screenshot": None,
        "script": (
            "Customer support teams face delayed replies, repetitive FAQ work, and weak after-hours coverage. "
            "Human agents spend too much time on shipping, returns, and account questions. Static FAQ pages "
            "only help when customers find the right article and use the same wording. Businesses also need "
            "answers grounded in their own policies — not a generic chatbot. That is the real-world problem "
            "we set out to solve."
        ),
    },
    {
        "num": 4,
        "title": "Project Objectives",
        "speaker": "Jatin Vaghela",
        "screenshot": None,
        "script": (
            "Our twelve-week objectives were clear. Build a hybrid chatbot using FAQ matching, NLP patterns, "
            "and local Ollama AI. Turn it into a multi-tenant SaaS with signup, businesses, and JWT auth. "
            "Let owners paste a free-text knowledge base with plan word limits. Add Stripe test billing for "
            "Basic, Professional, and Premium. Provide an embeddable website widget. And finish with "
            "demo-ready hosting and documentation. Next, Dev will show how the solution is structured."
        ),
    },
    # Dev 5-8
    {
        "num": 5,
        "title": "Solution: SupportFlow",
        "speaker": "Dev Bajaniya",
        "screenshot": None,
        "script": (
            "Thanks Jatin. I’m Dev Bajaniya, backend developer. SupportFlow is our solution. "
            "Business owners use a React dashboard to manage one or more businesses. They paste free-text "
            "knowledge, preview the chatbot, subscribe in Stripe test mode, and then embed a widget on their "
            "website so customers can chat. AI runs on local Ollama models, which keeps the demo stack under "
            "our control. We started as a single demo bot and evolved into a multi-business support platform."
        ),
    },
    {
        "num": 6,
        "title": "System Architecture",
        "speaker": "Dev Bajaniya",
        "screenshot": None,
        "script": (
            "At a high level, four blocks work together. The React dashboard and embed widget are the clients. "
            "The Flask API handles auth, chat, billing, and business APIs. The chatbot engine combines FAQ "
            "matching, retrieval-augmented knowledge, and Ollama generation. SQLite stores tenants, knowledge, "
            "sessions, and logs. Stripe test mode manages subscriptions, and for demos we expose the laptop "
            "through a Cloudflare or ngrok tunnel. This keeps UI, API, database, and AI in one coherent system."
        ),
    },
    {
        "num": 7,
        "title": "Backend & APIs",
        "speaker": "Dev Bajaniya",
        "screenshot": None,
        "script": (
            "On the backend we implemented JWT register and login, business and knowledge endpoints, "
            "chat plus streaming responses using server-sent events, and session history APIs. "
            "Billing endpoints cover checkout, portal, webhook, and confirm. We enforce plan limits in the API, "
            "serve widget.js and embed config, and in demo mode Flask also serves the built React SPA so one "
            "public URL hosts both frontend and API."
        ),
    },
    {
        "num": 8,
        "title": "Billing & Plan Limits",
        "speaker": "Dev Bajaniya",
        "screenshot": "Billing page (/billing) — show the three plan cards (Basic, Professional, Premium) and limits text.",
        "script": (
            "Billing uses Stripe in test mode. Plans are Free, Basic at five dollars, Professional at ten, "
            "and Premium at twenty Canadian dollars monthly. Limits control how many businesses you can create, "
            "how many knowledge words you can save, and whether Premium chat colors are unlocked. "
            "Checkout, confirmation, and webhooks keep subscription status in sync. "
            "Please look at the screenshot on this slide — it should be the Billing page with the plan cards. "
            "Next, Pratik will explain how data and testing support this."
        ),
    },
    # Pratik 9-12
    {
        "num": 9,
        "title": "Multi-Tenant Data Model",
        "speaker": "Pratik Chavda",
        "screenshot": None,
        "script": (
            "Hello, I’m Pratik Chavda, database manager. SupportFlow is multi-tenant. Each user can own "
            "businesses up to their plan cap. Knowledge is stored per business. Chat sessions and messages "
            "are scoped to that business so one tenant never sees another’s conversations. We also store "
            "subscription status, plan, and a widget key for public embed access. Isolation was a core "
            "design requirement throughout Weeks 8 to 12."
        ),
    },
    {
        "num": 10,
        "title": "Logging & Conversation History",
        "speaker": "Pratik Chavda",
        "screenshot": None,
        "script": (
            "Every chat stores user and bot messages with timestamps. We also keep which model was used, "
            "routing or intent information, and confidence where available. Free-tier preview chats are "
            "counted so limits can be enforced. Owners can reopen history in the dashboard sidebar, and "
            "website visitors can resume chats in the embed widget. Stats endpoints help owners see activity "
            "without exposing other tenants’ data."
        ),
    },
    {
        "num": 11,
        "title": "Testing & Quality",
        "speaker": "Pratik Chavda",
        "screenshot": None,
        "script": (
            "In Weeks 10 to 12 we focused on quality. We ran smoke tests from signup through chat and billing, "
            "API checks on core endpoints, multilingual probes, and greeting-versus-knowledge routing checks. "
            "We verified plan-limit rejections, embed key behavior, and that the public tunnel loads the UI "
            "instead of raw JSON. We also completed a final end-to-end regression before presentation. "
            "One lesson: older intent-only unit tests no longer match our RAG and AI-first design, so we "
            "relied on updated smoke and regression demos."
        ),
    },
    {
        "num": 12,
        "title": "Deployment (Demo Hosting)",
        "speaker": "Pratik Chavda",
        "screenshot": "Optional: browser showing the public tunnel URL on the SupportFlow landing page, or a terminal with cloudflared/ngrok.",
        "script": (
            "For faculty demos we host from a laptop. We build the React app and let Flask serve UI and API "
            "together. Ollama stays local. A Cloudflare or ngrok tunnel publishes port 5000. Stripe redirects "
            "must use that public URL. This is excellent for class demos, but we are honest that it is not "
            "yet a twenty-four-seven cloud production deploy. The screenshot placeholder can show the public "
            "link loading the landing page. Amal will now walk through the product UI."
        ),
    },
    # Amal 13-16
    {
        "num": 13,
        "title": "Owner Dashboard",
        "speaker": "Amal Satheesan",
        "screenshot": "Dashboard page (/dashboard) after login — business overview / navigation.",
        "script": (
            "Hi everyone, I’m Amal Satheesan, frontend and UI. This slide is the owner dashboard. "
            "After signup or login, owners land here to see their business context and navigate to knowledge, "
            "preview chat, billing, settings, and embed instructions. The screenshot should be the live "
            "Dashboard page. Our goal was a clean product UI — short labels, clear navigation — so the "
            "demo feels like a real SaaS, not a lab prototype only."
        ),
    },
    {
        "num": 14,
        "title": "Knowledge Base UI",
        "speaker": "Amal Satheesan",
        "screenshot": "Knowledge page (/knowledge) — text editor with word counter visible.",
        "script": (
            "On Knowledge, owners paste free-text business information — policies, products, FAQs, hours. "
            "The UI shows a live word count against the plan maximum so Free, Basic, Professional, and "
            "Premium limits are obvious before save. We also surface security warnings if the text looks "
            "risky. The screenshot on this slide should be the Knowledge editor with the counter visible. "
            "This page is what grounds the AI answers."
        ),
    },
    {
        "num": 15,
        "title": "Preview Chat & Embed Widget",
        "speaker": "Amal Satheesan",
        "screenshot": "Left: Preview Chat (/preview) with history sidebar. Right: embed widget on test.html (bubble open, History/New).",
        "script": (
            "Preview Chat lets owners test answers before going live, including streaming replies and a "
            "history sidebar for past conversations. The embed widget is what customers see on a website — "
            "a chat bubble with History and New chat controls, and optional Premium colors. "
            "Please look at both screenshots: preview on the left, widget on the right. Together they show "
            "the full owner-to-customer experience."
        ),
    },
    {
        "num": 16,
        "title": "Demo Path · Future · Thank You",
        "speaker": "Amal Satheesan",
        "screenshot": None,
        "script": (
            "To demo SupportFlow live, follow this path: sign up, create or open a business, paste knowledge, "
            "ask questions in preview chat, choose a Stripe test plan on Billing, then open the embed widget. "
            "For the future we want managed cloud hosting, a hosted model API for always-on AI, and stronger "
            "automated tests aligned to our RAG design. On behalf of Dev, Jatin, Pratik, and myself — thank you. "
            "We are happy to take questions."
        ),
    },
]


def build():
    doc = Document()

    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("SupportFlow — Final Presentation Speaking Script")
    r.bold = True
    r.font.size = Pt(16)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run(
        "AML-2404 / Group 2026S-AML-2403-OTT01-AI and ML Lab - 2\n"
        "Use with: Final-Presentation-SupportFlow.pptx\n"
        "Voice-over: each member records only their assigned slides, then merge into one PPT."
    )
    r.font.size = Pt(11)

    doc.add_heading("Voice-over assignment (equal split)", level=1)
    for line in [
        "Jatin Vaghela — Slides 1–4 (Title, Agenda, Problem, Objectives)",
        "Dev Bajaniya — Slides 5–8 (Solution, Architecture, Backend, Billing)",
        "Pratik Chavda — Slides 9–12 (Data model, Logging, Testing, Deployment)",
        "Amal Satheesan — Slides 13–16 (Dashboard, Knowledge, Chat/Embed, Closing)",
        "Dezosa is not included in this presentation.",
    ]:
        doc.add_paragraph(line, style="List Bullet")

    doc.add_heading("How to record (Microsoft guidance)", level=1)
    doc.add_paragraph(
        "In PowerPoint: Slide Show → Record. Record narration on your assigned slides only. "
        "Then combine everyone’s slides/timings into one file before submission. "
        "Official help: https://support.microsoft.com/en-us/office/record-a-slide-show-with-narration-and-slide-timings-0b9502c6-5f6c-40ae-b1e7-e47d8741161c"
    )
    doc.add_paragraph(
        "Tip: Paste real screenshots into the teal placeholder boxes before recording so you can "
        "say “as you can see on the screen…” naturally. Aim for about 45–70 seconds per slide."
    )

    doc.add_heading("Screenshot checklist (paste before recording)", level=1)
    for item in [
        "Slide 8 — /billing (plan cards)",
        "Slide 12 — optional public tunnel URL on landing page",
        "Slide 13 — /dashboard after login",
        "Slide 14 — /knowledge with word counter",
        "Slide 15 — /preview (history sidebar) AND embed widget (test.html)",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()
    doc.add_heading("Slide-by-slide narration", level=1)

    current_speaker = None
    for slide in SLIDES:
        if slide["speaker"] != current_speaker:
            current_speaker = slide["speaker"]
            doc.add_heading(f"Section: {current_speaker}", level=2)

        doc.add_heading(f"Slide {slide['num']}: {slide['title']}", level=3)
        p = doc.add_paragraph()
        r = p.add_run("Speaker: ")
        r.bold = True
        p.add_run(slide["speaker"])

        if slide["screenshot"]:
            p2 = doc.add_paragraph()
            r2 = p2.add_run("Screenshot to show: ")
            r2.bold = True
            r2.font.color.rgb = RGBColor(0x0B, 0x5F, 0x4B)
            p2.add_run(slide["screenshot"])

        p3 = doc.add_paragraph()
        r3 = p3.add_run("Say this:")
        r3.bold = True
        doc.add_paragraph(slide["script"])
        doc.add_paragraph("")  # spacer

    doc.add_heading("Suggested total runtime", level=1)
    doc.add_paragraph(
        "About 12–16 minutes of narration (roughly 45–60 seconds × 16 slides), plus optional live demo. "
        "Keep voice clear, pause briefly on screenshot slides, and do not read long paragraphs from the slide — "
        "slides are prompts; this document is the full script."
    )

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
