import duckdb
import sys
import os
from math import ceil

import voyageai

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def extract_products(jsonl_path: str) -> list[dict]:
    """Extract products from a JSONL file using DuckDB with filter criteria."""
    limit = config.SAMPLE_SIZE * 2
    completeness_min = config.COMPLETENESS_MIN

    sql = f"""
        SELECT
            code,
            product_name,
            brands,
            brands_tags,
            categories_tags,
            labels_tags,
            countries_tags,
            ingredients_text,
            nutriscore_grade,
            nova_group,
            image_url,
            image_small_url,
            "energy-kcal_100g",
            fat_100g,
            proteins_100g,
            sugars_100g,
            sodium_100g
        FROM read_ndjson('{jsonl_path}',
            ignore_errors=true,
            columns={{
                code: 'VARCHAR',
                product_name: 'VARCHAR',
                brands: 'VARCHAR',
                brands_tags: 'VARCHAR[]',
                categories_tags: 'VARCHAR[]',
                labels_tags: 'VARCHAR[]',
                countries_tags: 'VARCHAR[]',
                ingredients_text: 'VARCHAR',
                nutriscore_grade: 'VARCHAR',
                nova_group: 'DOUBLE',
                image_url: 'VARCHAR',
                image_small_url: 'VARCHAR',
                "energy-kcal_100g": 'DOUBLE',
                fat_100g: 'DOUBLE',
                proteins_100g: 'DOUBLE',
                sugars_100g: 'DOUBLE',
                sodium_100g: 'DOUBLE',
                completeness: 'DOUBLE'
            }}
        )
        WHERE list_contains(countries_tags, 'en:united-states')
          AND completeness >= {completeness_min}
          AND product_name IS NOT NULL
          AND product_name != ''
          AND image_url IS NOT NULL
          AND nutriscore_grade IS NOT NULL
        LIMIT {limit}
    """

    schema_fields = [
        "code", "product_name", "brands", "brands_tags", "categories_tags",
        "labels_tags", "countries_tags", "ingredients_text", "nutriscore_grade",
        "nova_group", "image_url", "image_small_url", "energy-kcal_100g",
        "fat_100g", "proteins_100g", "sugars_100g", "sodium_100g",
    ]

    con = duckdb.connect()
    result = con.execute(sql)
    col_names = [desc[0] for desc in result.description]
    rows = result.fetchall()
    con.close()

    products = []
    for row in rows:
        doc = dict(zip(col_names, row))
        filtered = {field: doc.get(field) for field in schema_fields}
        products.append(filtered)

    return products


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
