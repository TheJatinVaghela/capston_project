"""
AFTER refactor — excerpt from backend/app.py.

Word-limit enforcement and business_info seeding are shared helpers.
"""

def _knowledge_word_limit_response(text: str, effective: str, max_words: int):
    """
    Enforce plan knowledge word limits in one place.

    Returns (word_count, error_response_or_None).
    error_response is a (jsonify(...), status) tuple when over limit.
    """
    word_count = config.count_words(text)
    if word_count <= max_words:
        return word_count, None
    return word_count, (
        jsonify(
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
        ),
        403,
    )


def _seed_knowledge_business_info(knowledge: dict, biz: dict) -> dict:
    """Ensure knowledge embeds basic business identity fields."""
    info = knowledge.setdefault("business_info", {})
    if not isinstance(info, dict):
        info = {}
        knowledge["business_info"] = info
    info.setdefault("name", biz["name"])
    info.setdefault("website", biz.get("website") or "")
    info.setdefault("description", biz.get("description") or "")
    return knowledge


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
        word_count, limit_error = _knowledge_word_limit_response(
            text, effective, max_words
        )
        if limit_error:
            return limit_error
        warnings = security.knowledge_security_warnings(text)
        knowledge = _seed_knowledge_business_info(dict(biz.get("knowledge") or {}), biz)
        knowledge["text"] = text
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
    word_count = None
    if isinstance(knowledge.get("text"), str):
        knowledge["text"] = security.sanitize_knowledge_text(knowledge["text"])
        word_count, limit_error = _knowledge_word_limit_response(
            knowledge["text"], effective, max_words
        )
        if limit_error:
            return limit_error
    warnings = security.knowledge_security_warnings(knowledge.get("text") or "")
    knowledge = _seed_knowledge_business_info(knowledge, biz)
    info = knowledge.get("business_info") or {}
    biz = db.update_business(
        business_id,
        knowledge=knowledge,
        name=info.get("name") or biz["name"],
        website=info.get("website") or biz.get("website") or "",
        description=info.get("description") or biz.get("description") or "",
    )
    payload = {"business": db.public_business_view(biz), "warnings": warnings}
    if word_count is not None:
        payload["word_count"] = word_count
        payload["max_knowledge_words"] = max_words
    return jsonify(payload), 200
