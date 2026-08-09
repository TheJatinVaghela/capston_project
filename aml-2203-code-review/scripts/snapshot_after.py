from pathlib import Path

root = Path(__file__).resolve().parents[2]
text = (root / "backend" / "app.py").read_text(encoding="utf-8")
start = text.index("def _knowledge_word_limit_response")
marker = '@app.route("/businesses/<business_id>/settings"'
end = text.index(marker)
out = root / "aml-2203-code-review" / "after" / "update_knowledge_after.py"
header = (
    '"""\nAFTER refactor — excerpt from backend/app.py.\n\n'
    "Word-limit enforcement and business_info seeding are shared helpers.\n"
    '"""\n\n'
)
out.write_text(header + text[start:end].rstrip() + "\n", encoding="utf-8")
print(f"Wrote {out} ({end - start} chars)")
