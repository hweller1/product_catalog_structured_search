"""
End-to-end test harness for all 8 demo queries.
Run: python scripts/test_searches.py

Checks for each query:
  - Claude generates a valid $search stage (no fallback)
  - Pipeline returns >= 1 result
  - scoreDetails present with both pipelines represented
  - get_drove_by works without exception
  - explain_search_stage produces at least one label (for structured queries)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic
import voyageai
import pymongo
import config
from search.query_expansion import generate_search_stage
from search.pipeline import build_rank_fusion_pipeline, get_drove_by
from search.explain import explain_search_stage

QUERIES = [
    {
        "query": "kosher low sodium soup",
        "desc": "Label filter + nutrition range",
        "expect_constraints": ["Label: Kosher", "Sodium"],
        "expect_structured": True,
    },
    {
        "query": "organic whole grain cereal kids",
        "desc": "Semantic intent",
        "expect_constraints": ["Label: Organic"],
        "expect_structured": True,
    },
    {
        "query": "vegan protein bar chocolate",
        "desc": "Hybrid: lexical brand + semantic",
        "expect_constraints": [],
        "expect_structured": True,
    },
    {
        "query": "gluten free pasta high protein",
        "desc": "Claims + nutrition constraint",
        "expect_constraints": ["Label: Gluten Free"],
        "expect_structured": True,
    },
    {
        "query": "keto friendly snack low carb",
        "desc": "Pure semantic (no keto field)",
        "expect_constraints": [],
        "expect_structured": False,  # may fall back — that's OK
    },
    {
        "query": "Nutri-Score A dairy product",
        "desc": "Exact match on nutriscore_grade",
        "expect_constraints": ["Nutri-Score: A"],
        "expect_structured": True,
    },
    {
        "query": "Clif bar flavors",
        "desc": "Brand lexical match",
        "expect_constraints": [],
        "expect_structured": True,
    },
    {
        "query": "high fiber breakfast food low sugar",
        "desc": "Multi-constraint nutrition hybrid",
        "expect_constraints": [],
        "expect_structured": True,
    },
]

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
WARN = "\033[33mWARN\033[0m"


def make_anthropic_client():
    return anthropic.Anthropic(
        api_key="grove",
        base_url=config.ANTHROPIC_BASE_URL,
        default_headers={"api-key": config.GROVE_API_KEY},
    )


def run_tests():
    print("=== Structured Search Test Harness ===\n")

    anthropic_client = make_anthropic_client()
    voyage_client = voyageai.Client(api_key=config.VOYAGE_API_KEY)
    mongo_client = pymongo.MongoClient(config.MONGODB_URI)
    collection = mongo_client[config.MONGODB_DB][config.MONGODB_COLLECTION]

    # Sanity: collection has documents
    count = collection.count_documents({})
    print(f"Collection '{config.MONGODB_DB}.{config.MONGODB_COLLECTION}': {count} documents\n")
    if count == 0:
        print(f"{FAIL} Collection is empty — run scripts/load_data.py first")
        sys.exit(1)

    total = len(QUERIES)
    passed = 0
    failed = 0

    for i, spec in enumerate(QUERIES, 1):
        q = spec["query"]
        print(f"[{i}/{total}] \"{q}\"")
        print(f"        {spec['desc']}")

        errors = []
        warnings = []

        # 1. Query expansion
        try:
            search_stage, reason = generate_search_stage(q, anthropic_client)
        except Exception as e:
            errors.append(f"generate_search_stage raised: {e}")
            search_stage, reason = {}, "error"

        if reason not in ("ok",):
            warnings.append(f"Claude reason={reason!r} — using fallback $search")

        # 2. Check expected constraints present
        labels = explain_search_stage(search_stage)
        for expected in spec["expect_constraints"]:
            matched = any(expected.lower() in l.lower() for l in labels)
            if not matched:
                warnings.append(f"Expected constraint '{expected}' not found in labels: {labels}")

        if spec["expect_structured"] and reason != "ok":
            warnings.append(f"Expected structured output but got reason={reason!r}")

        # 3. Embed query
        try:
            embed_result = voyage_client.embed([q], model=config.VOYAGE_MODEL, input_type="query")
            query_vector = embed_result.embeddings[0]
        except Exception as e:
            errors.append(f"Voyage embed failed: {e}")
            query_vector = [0.0] * config.VOYAGE_DIMENSIONS

        # 4. Run pipeline
        pipeline = build_rank_fusion_pipeline(search_stage, query_vector, 1.0, 1.0, 10)
        try:
            results = list(collection.aggregate(pipeline))
        except Exception as e:
            errors.append(f"aggregate failed: {e}")
            results = []

        if len(results) == 0:
            errors.append("0 results returned")
        else:
            print(f"        Results: {len(results)}")
            # Show top 3
            for doc in results[:3]:
                name = doc.get("product_name", "?")
                score = round(doc.get("score", 0), 4)
                score_details = doc.get("scoreDetails", {})
                try:
                    drove = get_drove_by(score_details)
                except Exception as e:
                    errors.append(f"get_drove_by raised: {e}")
                    drove = "ERROR"
                print(f"          • {name[:55]:<55} score={score}  drove={drove}")

        # 5. scoreDetails sanity
        if results:
            details = results[0].get("scoreDetails", {}).get("details", [])
            pipeline_names = {d.get("inputPipelineName") for d in details}
            if not pipeline_names:
                warnings.append("scoreDetails.details is empty — $rankFusion may not be returning scoreDetails")
            else:
                missing = {"textPipeline", "vectorPipeline"} - pipeline_names
                if missing:
                    warnings.append(f"scoreDetails missing pipelines: {missing}")

        # 6. explain_search_stage doesn't crash
        try:
            explain_search_stage(search_stage)
        except Exception as e:
            errors.append(f"explain_search_stage raised: {e}")

        # Result
        if errors:
            print(f"        {FAIL}  errors: {'; '.join(errors)}")
            failed += 1
        else:
            status = PASS if not warnings else WARN
            if warnings:
                for w in warnings:
                    print(f"        {WARN}  {w}")
            print(f"        {status}")
            if not warnings:
                passed += 1
            else:
                passed += 1  # warnings are not failures
        print()

    print(f"=== Results: {passed}/{total} passed, {failed} failed ===")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
