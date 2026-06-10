import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import voyageai
import config

def embed_query(query: str) -> list[float]:
    client = voyageai.Client(api_key=config.VOYAGE_API_KEY)
    result = client.embed([query], model=config.VOYAGE_MODEL, input_type="query")
    return result.embeddings[0]
