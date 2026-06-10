"""MongoDB Atlas Search query expansion via Claude structured outputs."""

import sys
import os
import json
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import anthropic

SYSTEM_PROMPT = """You are a MongoDB Atlas Search query generator for a food product catalog.

## Schema
The product catalog has these indexed fields:
- product_name (string): product display name
- ingredients_text (string): raw ingredients list
- brands (string/array): manufacturer/brand name
- brands_tags (array): normalized brand tags
- labels_tags (array): certification/claim tags, e.g. "en:organic", "en:kosher", "en:gluten-free"
- categories_tags (array): product category tags, e.g. "en:cereals", "en:soups"
- nutriscore_grade (string): Nutri-Score letter a–e
- nova_group (number): NOVA processing group 1–4
- energy-kcal_100g (number): energy per 100g in kcal
- fat_100g (number): fat per 100g in grams
- proteins_100g (number): protein per 100g in grams
- sugars_100g (number): sugars per 100g in grams
- sodium_100g (number): sodium per 100g in grams (NOT mg)

## Operator Rules
- Text queries (product type, keywords) → "text" operator on product_name or ingredients_text
- Exact claims / boolean labels → "equals" operator on labels_tags or categories_tags
- Numeric constraints (low, high, less than) → "range" operator on nutrition fields (fat_100g, proteins_100g, sugars_100g, sodium_100g, energy-kcal_100g)
- Brand name queries → "text" operator on brands field

## Compound Clause Semantics
- "filter": hard constraints, zero score impact — use for certification tags (kosher, organic, vegan) and categorical restrictions
- "must": required match, affects score — use sparingly
- "should": optional boosting — use for soft preferences

## ONLY use field names from the schema above. Do not invent field names.

## Output Format
Return valid JSON for a MongoDB $search stage. Always include the "index" field set to "product_search_index". Use compound operator to combine multiple clauses.

## Examples

Example 1: "kosher low sodium soup"
{
  "index": "product_search_index",
  "compound": {
    "filter": [
      {"equals": {"path": "labels_tags", "value": "en:kosher"}},
      {"range": {"path": "sodium_100g", "lte": 0.12}}
    ],
    "should": [
      {"text": {"query": "soup", "path": "product_name"}}
    ]
  }
}

Example 2: "organic whole grain cereal"
{
  "index": "product_search_index",
  "compound": {
    "filter": [
      {"equals": {"path": "labels_tags", "value": "en:organic"}}
    ],
    "should": [
      {"text": {"query": "whole grain cereal", "path": "product_name"}},
      {"text": {"query": "whole grain", "path": "ingredients_text"}}
    ]
  }
}

## Hard Constraints
- NEVER use field names not listed in the schema above.
- ALWAYS include "index": "product_search_index" at the top level.
- Sodium stored in grams per 100g; "low sodium" threshold is ~0.12 g/100g (120mg).
- Use "en:" prefix for labels_tags and categories_tags values.
- Return only JSON, no explanation.
"""


ALLOWED_FIELDS = {
    "product_name",
    "ingredients_text",
    "brands",
    "brands_tags",
    "labels_tags",
    "categories_tags",
    "nutriscore_grade",
    "nova_group",
    "energy-kcal_100g",
    "fat_100g",
    "proteins_100g",
    "sugars_100g",
    "sodium_100g",
}


def _strip_unknown_fields(stage: dict, allowed: set) -> dict:
    """Remove $search clauses that reference fields not in allowed set."""
    import copy
    stage = copy.deepcopy(stage)

    def clean_clause_list(clauses: list) -> list:
        result = []
        for clause in clauses:
            if not isinstance(clause, dict):
                result.append(clause)
                continue
            has_unknown = False
            for op_val in clause.values():
                if isinstance(op_val, dict) and "path" in op_val:
                    path = op_val["path"]
                    if isinstance(path, str) and path not in allowed:
                        has_unknown = True
                        break
                    elif isinstance(path, list) and any(p not in allowed for p in path):
                        has_unknown = True
                        break
            if not has_unknown:
                result.append(clause)
        return result

    if "compound" in stage:
        compound = stage["compound"]
        for key in ["filter", "must", "should", "mustNot"]:
            if key in compound:
                compound[key] = clean_clause_list(compound[key])

    return stage


def sanitize_search_stage(stage: dict, query: str = "") -> dict:
    """Sanitize a Claude-generated $search stage."""
    stage["index"] = config.INDEX_SEARCH_NAME
    stage = _strip_unknown_fields(stage, ALLOWED_FIELDS)

    if "compound" in stage:
        compound = stage["compound"]
        has_clauses = any(
            compound.get(k) for k in ["filter", "must", "should", "mustNot"]
        )
        if not has_clauses:
            return fallback_search_stage(query)

    return stage


def generate_search_stage(query: str, client=None) -> tuple:
    """Generate a MongoDB $search stage using Claude structured outputs."""
    if client is None:
        client = anthropic.Anthropic(
            api_key="grove",
            base_url=config.ANTHROPIC_BASE_URL,
            default_headers={"api-key": config.GROVE_API_KEY},
        )
    try:
        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            temperature=0.0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f'Query: "{query}"'}],
        )
        if response.stop_reason == "refusal":
            return (fallback_search_stage(query), "refusal")
        try:
            raw = response.content[0].text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()
            stage = json.loads(raw)
        except (json.JSONDecodeError, IndexError):
            return (fallback_search_stage(query), "json_error")
        sanitized = sanitize_search_stage(stage, query)
        return (sanitized, "ok")
    except anthropic.APIError as e:
        logging.warning(f"Claude API error: {e}")
        return (fallback_search_stage(query), "error")
    except Exception:
        return (fallback_search_stage(query), "error")


def fallback_search_stage(query: str) -> dict:
    """Return a simple text search stage for fallback when LLM expansion fails."""
    return {
        "index": config.INDEX_SEARCH_NAME,
        "text": {"query": query, "path": "product_name"},
    }
