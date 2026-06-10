"""Translate a Claude-generated $search stage into human-readable constraint labels."""

_FIELD_LABELS = {
    "labels_tags": ("Label", lambda v: v.replace("en:", "").replace("-", " ").title()),
    "categories_tags": ("Category", lambda v: v.replace("en:", "").replace("-", " ").title()),
    "brands_tags": ("Brand", lambda v: v.replace("en:", "").replace("-", " ").title()),
    "brands": ("Brand", lambda v: v.title()),
    "nutriscore_grade": ("Nutri-Score", lambda v: v.upper()),
    "nova_group": ("NOVA group", str),
}

_NUTRITION_FIELDS = {
    "sodium_100g": ("Sodium", lambda v: f"{round(v * 1000)}mg"),
    "energy-kcal_100g": ("Calories", lambda v: f"{round(v)}kcal"),
    "proteins_100g": ("Protein", lambda v: f"{v}g"),
    "fat_100g": ("Fat", lambda v: f"{v}g"),
    "sugars_100g": ("Sugar", lambda v: f"{v}g"),
}


def _equals_label(path: str, value) -> str:
    if path in _FIELD_LABELS:
        label, fmt = _FIELD_LABELS[path]
        return f"{label}: {fmt(str(value))}"
    return f"{path}: {value}"


def _range_label(path: str, r: dict) -> str:
    if path in _NUTRITION_FIELDS:
        label, fmt = _NUTRITION_FIELDS[path]
    else:
        label, fmt = path, str

    parts = []
    if "gte" in r:
        parts.append(f"≥ {fmt(r['gte'])}")
    if "gt" in r:
        parts.append(f"> {fmt(r['gt'])}")
    if "lte" in r:
        parts.append(f"≤ {fmt(r['lte'])}")
    if "lt" in r:
        parts.append(f"< {fmt(r['lt'])}")

    return f"{label} {' '.join(parts)}"


def _clause_labels(clause: dict) -> list[str]:
    if "equals" in clause:
        eq = clause["equals"]
        return [_equals_label(eq.get("path", ""), eq.get("value", ""))]
    if "range" in clause:
        r = clause["range"]
        path = r.get("path", "")
        return [_range_label(path, {k: v for k, v in r.items() if k != "path"})]
    if "text" in clause:
        q = clause["text"].get("query", "")
        return [f'Keyword: "{q}"'] if q else []
    if "phrase" in clause:
        q = clause["phrase"].get("query", "")
        return [f'Phrase: "{q}"'] if q else []
    return []


def explain_search_stage(stage: dict) -> list[str]:
    """Return human-readable constraint strings from a $search stage."""
    if not stage:
        return []

    # Simple text fallback (no compound)
    if "text" in stage and "compound" not in stage:
        q = stage["text"].get("query", "")
        return [f'Keyword: "{q}"'] if q else []

    labels = []
    compound = stage.get("compound", {})
    for clause_type in ("filter", "must", "should", "mustNot"):
        for clause in compound.get(clause_type, []):
            labels.extend(_clause_labels(clause))
    return labels
