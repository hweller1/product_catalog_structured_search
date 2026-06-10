import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from pymongo.operations import SearchIndexModel


def create_search_index(collection) -> None:
    print("Creating Atlas Search index...")

    index_definition = {
        "name": config.INDEX_SEARCH_NAME,
        "type": "search",
        "definition": {
            "mappings": {
                "dynamic": False,
                "fields": {
                    "product_name": {"type": "string", "analyzer": "lucene.standard"},
                    "ingredients_text": {"type": "string", "analyzer": "lucene.standard"},
                    "brands": [
                        {"type": "string", "analyzer": "lucene.standard"},
                        {"type": "token"}
                    ],
                    "categories_tags": {"type": "token"},
                    "labels_tags": {"type": "token"},
                    "nutriscore_grade": {"type": "token"},
                    "nova_group": {"type": "number"},
                    "energy-kcal_100g": {"type": "number"},
                    "fat_100g": {"type": "number"},
                    "proteins_100g": {"type": "number"},
                    "sugars_100g": {"type": "number"},
                    "sodium_100g": {"type": "number"}
                }
            }
        }
    }

    # Drop existing index if it exists
    for idx in collection.list_search_indexes():
        if idx.get("name") == config.INDEX_SEARCH_NAME:
            collection.drop_search_index(config.INDEX_SEARCH_NAME)
            break

    # Create index
    collection.create_search_index(model=index_definition)


def create_vector_index(collection) -> None:
    print("Creating Atlas Vector Search index...")
    # Drop existing if it exists
    for idx in collection.list_search_indexes():
        if idx.get("name") == config.INDEX_VECTOR_NAME:
            collection.drop_search_index(config.INDEX_VECTOR_NAME)
            break
    vector_index = SearchIndexModel(
        definition={
            "fields": [
                {"type": "vector", "path": "embedding", "numDimensions": 1024, "similarity": "cosine"},
                {"type": "filter", "path": "labels_tags"},
                {"type": "filter", "path": "brands_tags"},
                {"type": "filter", "path": "categories_tags"},
                {"type": "filter", "path": "nutriscore_grade"}
            ]
        },
        name=config.INDEX_VECTOR_NAME,
        type="vectorSearch"
    )
    collection.create_search_index(model=vector_index)


def wait_for_indexes(collection, timeout_seconds: int = 300) -> None:
    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Indexes not READY after {timeout_seconds}s")
        indexes = {idx["name"]: idx.get("status") for idx in collection.list_search_indexes()}
        search_ready = indexes.get(config.INDEX_SEARCH_NAME) == "READY"
        vector_ready = indexes.get(config.INDEX_VECTOR_NAME) == "READY"
        if search_ready and vector_ready:
            print("Both indexes READY")
            return
        print(f"Waiting for indexes... ({elapsed}s)")
        time.sleep(5)
