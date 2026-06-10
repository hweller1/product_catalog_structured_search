import gzip
import json as _json
import sys
import os
from math import ceil

import voyageai

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

_SCHEMA_FIELDS = [
    "code", "product_name", "brands", "brands_tags", "categories_tags",
    "labels_tags", "countries_tags", "ingredients_text", "nutriscore_grade",
    "nova_group", "image_url", "image_small_url", "energy-kcal_100g",
    "fat_100g", "proteins_100g", "sugars_100g", "sodium_100g",
]


def extract_products(jsonl_path: str) -> list[dict]:
    """Stream-filter products from JSONL(.gz) without loading the full file.

    DuckDB schema auto-detection is unreliable on the large OFF file when
    field types are inconsistent across rows. Streaming in Python is safer
    and fast enough — we typically find 2000 qualifying products well before
    scanning the full file.
    """
    limit = config.SAMPLE_SIZE * 2
    completeness_min = config.COMPLETENESS_MIN

    docs: list[dict] = []
    scanned = 0
    open_fn = gzip.open if jsonl_path.endswith(".gz") else open

    with open_fn(jsonl_path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if len(docs) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            scanned += 1
            if scanned % 100_000 == 0:
                print(f"  Scanned {scanned:,} rows, {len(docs)} matched so far...", end="\r")
            try:
                doc = _json.loads(line)
            except Exception:
                continue

            countries = doc.get("countries_tags")
            if not isinstance(countries, list) or "en:united-states" not in countries:
                continue
            if (doc.get("completeness") or 0) < completeness_min:
                continue
            if not (doc.get("product_name") or "").strip():
                continue
            if not doc.get("nutriscore_grade"):
                continue

            docs.append({f: doc.get(f) for f in _SCHEMA_FIELDS})

    print(f"\n  Scanned {scanned:,} rows, extracted {len(docs)} products.")
    return docs


def product_to_prose(doc: dict) -> str:
    parts = []
    if doc.get("product_name"):
        parts.append(f"Product: {doc['product_name']}")
    if doc.get("brands"):
        parts.append(f"Brand: {doc['brands']}")
    if doc.get("categories_tags"):
        cats = [t.replace("en:", "") for t in doc["categories_tags"][-2:]]
        parts.append(f"Category: {', '.join(cats)}")
    if doc.get("labels_tags"):
        labels = [t.replace("en:", "") for t in doc["labels_tags"]]
        parts.append(f"Labels: {', '.join(labels)}")
    ingredients_text = doc.get("ingredients_text") or ""
    if ingredients_text.strip():
        parts.append(f"Ingredients: {ingredients_text[:300]}")
    if doc.get("nutriscore_grade"):
        parts.append(f"Nutri-Score: {doc['nutriscore_grade'].upper()}")
    nutrition = []
    if doc.get("proteins_100g"):
        nutrition.append(f"protein {doc['proteins_100g']}g")
    if doc.get("sodium_100g"):
        nutrition.append(f"sodium {round(doc['sodium_100g'] * 1000)}mg")
    if doc.get("sugars_100g"):
        nutrition.append(f"sugar {doc['sugars_100g']}g")
    if nutrition:
        parts.append(f"Nutrition per 100g: {', '.join(nutrition)}")
    if doc.get("nova_group") is not None:
        parts.append(f"NOVA group: {doc['nova_group']}")
    return ". ".join(parts)


def embed_documents(docs: list[dict]) -> list[list[float]]:
    """Batch embed documents using Voyage AI."""
    client = voyageai.Client(api_key=config.VOYAGE_API_KEY)
    texts = [product_to_prose(doc) for doc in docs]
    batch_size = config.EMBED_BATCH_SIZE
    total = len(texts)
    embeddings = []

    for i in range(0, total, batch_size):
        batch = texts[i:i + batch_size]
        print(f"Embedding batch {i // batch_size + 1}/{ceil(total / batch_size)}")
        result = client.embed(batch, model=config.VOYAGE_MODEL, input_type="document")
        embeddings.extend(result.embeddings)

    return embeddings


def load_to_atlas(docs: list[dict], embeddings: list[list[float]]) -> int:
    import pymongo
    for doc, emb in zip(docs, embeddings):
        doc["embedding"] = emb
    client = pymongo.MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB]
    collection = db[config.MONGODB_COLLECTION]
    collection.drop()
    result = collection.insert_many(docs)
    count = len(result.inserted_ids)
    print(f"Inserted {count} products into {config.MONGODB_DB}.{config.MONGODB_COLLECTION}")
    client.close()
    return count
