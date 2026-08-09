"""
BEFORE refactor — excerpt from backend/app.py (update_knowledge).

Duplicated plan word-limit error payloads and repeated business_info seeding
lived inline in both free-text and legacy structured branches.
"""

@app.route("/businesses/<business_id>/knowledge", methods=["PUT"])
@require_business_owner
def update_knowledge(business_id):
    data = request.get_json(silent=True) or {}
    biz = request.current_business
    effective = config.effective_plan_id(biz.get("plan"), biz.get("subscription_status"))
    limits = config.plan_limits(effective)
    max_words = limits["max_knowledge_words"]

    # Free-text knowledge (preferred)
    if "text" in data or "knowledge_text" in data:
        text = data.get("text")
        if text is None:
            text = data.get("knowledge_text")
        if not isinstance(text, str):
            return jsonify({"error": "text must be a string"}), 400
        text = security.sanitize_knowledge_text(text)
        word_count = config.count_words(text)
        if word_count > max_words:
            return jsonify(
                {
                    "error": (
                        f"Knowledge is {word_count} words; your "
                        f"{effective.title()} plan allows {max_words} words. "
                        "Shorten the text or upgrade on Billing."
                    ),
                    "word_count": word_count,
                    "max_knowledge_words": max_words,
                    "effective_plan": effective,
                }
            ), 403
        warnings = security.knowledge_security_warnings(text)
        knowledge = dict(biz.get("knowledge") or {})
        knowledge["text"] = text
        knowledge.setdefault("business_info", {})
        knowledge["business_info"].setdefault("name", biz["name"])
        knowledge["business_info"].setdefault("website", biz.get("website") or "")
        knowledge["business_info"].setdefault(
            "description", biz.get("description") or ""
        )
        biz = db.update_business(business_id, knowledge=knowledge)
        return jsonify(
            {
                "business": db.public_business_view(biz),
                "warnings": warnings,
                "word_count": word_count,
                "max_knowledge_words": max_words,
            }
        ), 200

    # Legacy structured object
    knowledge = data.get("knowledge")
    if not isinstance(knowledge, dict):
        return jsonify({"error": "Provide text (string) or knowledge (object)"}), 400
    if isinstance(knowledge.get("text"), str):
        knowledge["text"] = security.sanitize_knowledge_text(knowledge["text"])
        word_count = config.count_words(knowledge["text"])
        if word_count > max_words:
            return jsonify(
                {
                    "error": (
                        f"Knowledge is {word_count} words; your "
                        f"{effective.title()} plan allows {max_words} words. "
                        "Shorten the text or upgrade on Billing."
                    ),
                    "word_count": word_count,
                    "max_knowledge_words": max_words,
                    "effective_plan": effective,
                }
            ), 403
    warnings = security.knowledge_security_warnings(knowledge.get("text") or "")
    info = knowledge.setdefault("business_info", {})
    info.setdefault("name", biz["name"])
    biz = db.update_business(
        business_id,
        knowledge=knowledge,
        name=info.get("name") or biz["name"],
        website=info.get("website") or biz.get("website") or "",
        description=info.get("description") or biz.get("description") or "",
    )
    return jsonify({"business": db.public_business_view(biz), "warnings": warnings}), 200
