import os
from dotenv import load_dotenv

load_dotenv()

# Required env vars — hard-fail at import time if missing
MONGODB_URI = os.environ["MONGODB_URI"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
VOYAGE_API_KEY = os.environ["VOYAGE_API_KEY"]

# Optional env vars with defaults
MONGODB_DB = os.environ.get("MONGODB_DB", "structured_search")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "products")

# Model constants
CLAUDE_MODEL = "claude-haiku-4-5"
VOYAGE_MODEL = "voyage-4"
VOYAGE_DIMENSIONS = 1024
EMBED_BATCH_SIZE = 128

# Index name constants
INDEX_SEARCH_NAME = "product_search_index"
INDEX_VECTOR_NAME = "product_vector_index"

# Data constants
SAMPLE_SIZE = 1000
COMPLETENESS_MIN = 0.7
