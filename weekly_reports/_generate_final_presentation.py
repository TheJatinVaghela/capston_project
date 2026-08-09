"""
Generate AML-2404 Final Presentation (16 slides, 4 members × 4 slides).
Point-based slides with screenshot placeholders — not text-heavy.
"""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

OUT = r"D:\customer-service-chatbot\weekly_reports\Final-Presentation-SupportFlow.pptx"

# SupportFlow-ish palette (avoid generic purple AI look)
NAVY = RGBColor(0x0B, 0x1F, 0x33)
TEAL = RGBColor(0x2D, 0xD4, 0xBF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xE8, 0xEE, 0xF5)
MUTED = RGBColor(0x9A, 0xB0, 0xC4)
CARD = RGBColor(0x12, 0x30, 0x47)
ACCENT = RGBColor(0x3D, 0x8B, 0xFD)


def set_run(run, size=18, bold=False, color=WHITE, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"


def add_bg(slide, color=NAVY):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    # send to back
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)
    return shape


def add_accent_bar(slide):
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.12), Inches(7.5)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def add_footer(slide, page, speaker):
    box = slide.shapes.add_textbox(Inches(0.4), Inches(7.05), Inches(10), Inches(0.35))
    tf = box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = f"SupportFlow  ·  AML-2404  ·  Slide {page}/16  ·  Voice: {speaker}"
    set_run(run, size=11, color=MUTED)

    box2 = slide.shapes.add_textbox(Inches(10.5), Inches(7.05), Inches(2.5), Inches(0.35))
    tf2 = box2.text_frame
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.RIGHT
    run2 = p2.add_run()
    run2.text = "Lambton College"
    set_run(run2, size=11, color=MUTED)


def title_text(slide, text, top=0.35, size=32):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(12.2), Inches(0.7))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=True, color=WHITE)
    return box


def subtitle(slide, text, top=1.0, size=16, color=TEAL):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(12.2), Inches(0.4))
    tf = box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    set_run(run, size=size, color=color, italic=False)
    return box


def bullets(slide, items, left=0.55, top=1.6, width=12.0, size=20):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(5.0))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(12)
        run = p.add_run()
        run.text = f"•  {item}"
        set_run(run, size=size, color=LIGHT)
    return box


def screenshot_placeholder(slide, label, left, top, width, height):
    """Empty frame telling the team which app page to paste."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = TEAL
    shape.line.width = Pt(1.5)

    # dashed-feel via inner text only
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "📸 SCREENSHOT PLACEHOLDER"
    set_run(run, size=14, bold=True, color=TEAL)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(8)
    run2 = p2.add_run()
    run2.text = label
    set_run(run2, size=13, color=LIGHT)

    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(6)
    run3 = p3.add_run()
    run3.text = "Paste image here before recording voice-over"
    set_run(run3, size=11, color=MUTED, italic=True)
    return shape


def two_column_bullets(slide, left_items, right_items, top=1.7):
    bullets(slide, left_items, left=0.55, top=top, width=5.8, size=18)
    bullets(slide, right_items, left=6.8, top=top, width=5.8, size=18)


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # Speaker map for footers
    # Jatin 1-4, Dev 5-8, Pratik 9-12, Amal 13-16

    # ── 1 Title ────────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "SupportFlow", top=2.0, size=44)
    subtitle(s, "AI-Powered Customer Service Chatbot  →  Multi-Tenant SaaS", top=2.75, size=20)
    box = s.shapes.add_textbox(Inches(0.55), Inches(3.5), Inches(12), Inches(1.5))
    tf = box.text_frame
    lines = [
        "AML-2404 · AI and ML Lab · Lambton College",
        "Final Presentation  ·  Group: 2026S-AML-2403-OTT01-AI and ML Lab - 2",
        "Dev Bajaniya  ·  Jatin Vaghela  ·  Pratik Chavda  ·  Amal Satheesan",
        "Faculty Supervisor: William Pourmajidi",
    ]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = line
        set_run(run, size=15, color=MUTED if i else LIGHT)
    add_footer(s, 1, "Jatin")

    # ── 2 Agenda ───────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Agenda")
    subtitle(s, "What we will cover today")
    two_column_bullets(
        s,
        [
            "Problem & objectives",
            "Solution overview",
            "Architecture & AI pipeline",
            "Multilingual & guardrails",
        ],
        [
            "Data model & testing",
            "Product walkthrough (UI)",
            "Billing, embed & hosting",
            "Demo path · Future work · Q&A",
        ],
        top=1.8,
    )
    add_footer(s, 2, "Jatin")

    # ── 3 Problem ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "The Problem")
    subtitle(s, "Why customer support needs intelligent automation")
    bullets(
        s,
        [
            "Delayed replies to repetitive questions",
            "Agents overloaded with shipping / returns / FAQ work",
            "Limited after-hours coverage",
            "Static FAQ pages fail when wording changes",
            "Businesses need owned knowledge — not a generic chatbot",
        ],
        top=1.7,
        size=22,
    )
    add_footer(s, 3, "Jatin")

    # ── 4 Objectives ───────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Project Objectives")
    subtitle(s, "What we set out to build in 12 weeks")
    bullets(
        s,
        [
            "Hybrid chatbot: FAQ + NLP patterns + local AI (Ollama)",
            "Multi-tenant SaaS: signup, businesses, JWT auth",
            "Owner knowledge base with plan word limits",
            "Stripe test billing (Basic / Pro / Premium)",
            "Embeddable widget for customer websites",
            "Demo-ready hosting + documentation",
        ],
        top=1.65,
        size=20,
    )
    add_footer(s, 4, "Jatin")

    # ── 5 Solution Overview ────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Solution: SupportFlow")
    subtitle(s, "From single demo bot → multi-business support platform")
    bullets(
        s,
        [
            "Owners manage businesses in a React dashboard",
            "Paste free-text knowledge → AI answers from that knowledge",
            "Preview chat before going live",
            "Subscribe → unlock embed widget",
            "Customers chat on the owner’s website",
            "Local Ollama models keep AI on our stack for demos",
        ],
        top=1.65,
        size=20,
    )
    add_footer(s, 5, "Dev")

    # ── 6 Architecture ─────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "System Architecture")
    subtitle(s, "High-level components (no code dump)")

    # architecture cards
    cards = [
        (0.55, "React Dashboard\n+ Embed Widget"),
        (3.7, "Flask API\nAuth · Chat · Billing"),
        (6.85, "Chatbot Engine\nFAQ · RAG · Ollama"),
        (10.0, "SQLite\nTenants · Logs"),
    ]
    for left, text in cards:
        shape = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(2.0), Inches(2.9), Inches(2.2)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = CARD
        shape.line.color.rgb = TEAL
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = text
        set_run(run, size=16, bold=True, color=WHITE)

    bullets(
        s,
        [
            "Stripe (test mode) for subscriptions",
            "Tunnel (Cloudflare / ngrok) for shared demo URL",
        ],
        top=4.6,
        size=18,
    )
    add_footer(s, 6, "Dev")

    # ── 7 Backend & APIs ───────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Backend & APIs")
    subtitle(s, "Flask services that power the product")
    two_column_bullets(
        s,
        [
            "JWT auth (register / login / me)",
            "Businesses & knowledge APIs",
            "Chat + streaming (SSE)",
            "Session history APIs",
        ],
        [
            "Stripe checkout / portal / webhook",
            "Plan limit enforcement",
            "Embed config + widget.js",
            "SPA serving for public demo",
        ],
        top=1.8,
    )
    add_footer(s, 7, "Dev")

    # ── 8 Billing ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Billing & Plan Limits")
    subtitle(s, "Stripe test mode · feature gates by plan")
    bullets(
        s,
        [
            "Free → Basic ($5) → Professional ($10) → Premium ($20)",
            "Limits: businesses · knowledge words · Premium colors",
            "Checkout + confirm + webhook sync",
        ],
        left=0.55,
        top=1.55,
        width=6.0,
        size=17,
    )
    screenshot_placeholder(
        s,
        "APP PAGE: Billing\n(/billing — plan cards Basic / Pro / Premium)",
        left=7.0,
        top=1.55,
        width=5.7,
        height=4.8,
    )
    add_footer(s, 8, "Dev")

    # ── 9 Data Model ───────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Multi-Tenant Data Model")
    subtitle(s, "SQLite schema that keeps businesses isolated")
    bullets(
        s,
        [
            "Users → own many Businesses (plan-capped)",
            "Knowledge stored per business",
            "Sessions & messages scoped to business",
            "Subscription status + plan fields",
            "Widget key for public embed access",
            "No cross-tenant chat leakage",
        ],
        top=1.65,
        size=20,
    )
    add_footer(s, 9, "Pratik")

    # ── 10 Logging & Analytics ─────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Logging & Conversation History")
    subtitle(s, "What we store for demos, analytics, and resume-chat")
    bullets(
        s,
        [
            "User + bot messages with timestamps",
            "Model used · intent/route · confidence",
            "Preview chat counters for free tier",
            "History sidebar (dashboard) + widget history",
            "Stats for owners (session activity)",
        ],
        top=1.7,
        size=20,
    )
    add_footer(s, 10, "Pratik")

    # ── 11 Testing ─────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Testing & Quality")
    subtitle(s, "How we validated the system (Weeks 10–12)")
    two_column_bullets(
        s,
        [
            "Smoke: signup → chat → billing",
            "API checks on core endpoints",
            "Multilingual probe utterances",
            "Greeting vs knowledge routing",
        ],
        [
            "Plan limit rejection checks",
            "Embed key + origin checks",
            "Tunnel SPA load verification",
            "Final end-to-end regression",
        ],
        top=1.8,
    )
    add_footer(s, 11, "Pratik")

    # ── 12 Deployment ──────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Deployment (Demo Hosting)")
    subtitle(s, "Laptop as host · public link via tunnel")
    bullets(
        s,
        [
            "Build React → Flask serves UI + API together",
            "Ollama stays local on the laptop",
            "Cloudflare / ngrok tunnel to port 5000",
            "Stripe redirects use public FRONTEND_URL",
            "Honest limit: great for demos, not 24/7 cloud yet",
        ],
        left=0.55,
        top=1.55,
        width=6.2,
        size=17,
    )
    screenshot_placeholder(
        s,
        "OPTIONAL: Terminal / browser\nshowing public tunnel URL\nloading SupportFlow landing",
        left=7.0,
        top=1.55,
        width=5.7,
        height=4.8,
    )
    add_footer(s, 12, "Pratik")

    # ── 13 Dashboard UX ────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Owner Dashboard")
    subtitle(s, "Where businesses manage support AI")
    bullets(
        s,
        [
            "Landing · Login / Signup",
            "Dashboard overview",
            "Business switcher",
        ],
        left=0.55,
        top=1.55,
        width=5.5,
        size=18,
    )
    screenshot_placeholder(
        s,
        "APP PAGE: Dashboard\n(/dashboard — after login)",
        left=6.3,
        top=1.45,
        width=6.4,
        height=5.0,
    )
    add_footer(s, 13, "Amal")

    # ── 14 Knowledge ───────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Knowledge Base UI")
    subtitle(s, "Owners paste business truth · word counter by plan")
    bullets(
        s,
        [
            "Free-text knowledge editor",
            "Live word count vs plan max",
            "Security warnings for risky text",
        ],
        left=0.55,
        top=1.55,
        width=5.5,
        size=18,
    )
    screenshot_placeholder(
        s,
        "APP PAGE: Knowledge\n(/knowledge — editor + word counter)",
        left=6.3,
        top=1.45,
        width=6.4,
        height=5.0,
    )
    add_footer(s, 14, "Amal")

    # ── 15 Chat + Embed ────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Preview Chat & Embed Widget")
    subtitle(s, "Try before go-live · then put chat on any site")
    screenshot_placeholder(
        s,
        "APP PAGE: Preview Chat\n(/preview — history sidebar + streaming)",
        left=0.45,
        top=1.45,
        width=6.0,
        height=5.0,
    )
    screenshot_placeholder(
        s,
        "APP PAGE: Embed / test.html\n(widget bubble + History / New chat)",
        left=6.8,
        top=1.45,
        width=6.0,
        height=5.0,
    )
    add_footer(s, 15, "Amal")

    # ── 16 Close ───────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_accent_bar(s)
    title_text(s, "Demo Path · Future · Thank You")
    subtitle(s, "Closing the 12-week journey")
    two_column_bullets(
        s,
        [
            "Demo: Signup → Knowledge → Chat",
            "Then: Billing → Embed widget",
            "Future: cloud host + hosted model",
            "Future: stronger automated tests",
        ],
        [
            "Team: Dev · Jatin · Pratik · Amal",
            "Course: AML-2404 / AI & ML Lab",
            "Questions welcome",
            "Thank you!",
        ],
        top=1.75,
    )
    add_footer(s, 16, "Amal")

    # Notes on each slide with speaker cue (optional for PPT notes)
    speakers = (
        ["Jatin"] * 4 + ["Dev"] * 4 + ["Pratik"] * 4 + ["Amal"] * 4
    )
    for i, slide in enumerate(prs.slides):
        notes = slide.notes_slide.notes_text_frame
        notes.text = (
            f"Voice-over owner: {speakers[i]}  |  See Final-Presentation-Speaking-Script.docx "
            f"for full narration of slide {i + 1}."
        )

    prs.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
