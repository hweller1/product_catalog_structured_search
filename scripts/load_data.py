import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import pymongo
from data.loader import extract_products, embed_documents, load_to_atlas
from data.indexer import create_search_index, create_vector_index, wait_for_indexes

DUMP_URL = "https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz"
DUMP_FILE = "openfoodfacts-products.jsonl.gz"


def download_dump():
    print(f"Downloading {DUMP_URL} ...")
    response = requests.get(DUMP_URL, stream=True, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    with open(DUMP_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"  {pct:.1f}% ({downloaded // (1024*1024)} MB)", end="\r")
    print(f"\nDownload complete: {downloaded // (1024*1024)} MB")


if __name__ == "__main__":
    # Step 1: Download if needed
    if not os.path.exists(DUMP_FILE):
        download_dump()
    else:
        print(f"Found existing {DUMP_FILE}, skipping download")

    # Step 2: Extract
    print("Extracting products...")
    docs = extract_products(DUMP_FILE)
    print(f"Extracted {len(docs)} products")

    # Step 3: Embed
    print("Embedding products...")
    embeddings = embed_documents(docs)

    # Step 4: Load to Atlas
    count = load_to_atlas(docs, embeddings)

    # Step 5: Create indexes
    client = pymongo.MongoClient(config.MONGODB_URI)
    collection = client[config.MONGODB_DB][config.MONGODB_COLLECTION]
    create_search_index(collection)
    create_vector_index(collection)
    wait_for_indexes(collection)
    client.close()

    print(f"Done! {count} products loaded and indexes READY.")
