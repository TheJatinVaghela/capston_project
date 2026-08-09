from pathlib import Path

root = Path(__file__).resolve().parents[2]
text = (root / "backend" / "app.py").read_text(encoding="utf-8")
start = text.index("def update_knowledge(business_id):")
start = text.rfind("@app.route", 0, start)
end = text.index('@app.route("/businesses/<business_id>/settings"')
out = root / "aml-2203-code-review" / "before" / "update_knowledge_before.py"
out.write_text(text[start:end].rstrip() + "\n", encoding="utf-8")
print(f"Wrote {out} ({end - start} chars)")
