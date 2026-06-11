import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import voyageai
import pymongo

import config
from search.query_expansion import generate_search_stage
from search.pipeline import build_rank_fusion_pipeline, get_drove_by
from search.explain import explain_search_stage

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_anthropic = anthropic.Anthropic(
    api_key="grove",
    base_url=config.ANTHROPIC_BASE_URL,
    default_headers={"api-key": config.GROVE_API_KEY},
)
_voyage = voyageai.Client(api_key=config.VOYAGE_API_KEY)
_mongo = pymongo.MongoClient(config.MONGODB_URI)
_collection = _mongo[config.MONGODB_DB][config.MONGODB_COLLECTION]


class SearchRequest(BaseModel):
    query: str
    text_weight: float = 1.0
    vector_weight: float = 1.0
    top_k: int = 10


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/search")
def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    search_stage, reason = generate_search_stage(req.query, _anthropic)

    embed_result = _voyage.embed([req.query], model=config.VOYAGE_MODEL, input_type="query")
    query_vector = embed_result.embeddings[0]

    pipeline = build_rank_fusion_pipeline(
        search_stage, query_vector, req.text_weight, req.vector_weight, req.top_k
    )

    raw_results = list(_collection.aggregate(pipeline))

    results = []
    for doc in raw_results:
        score_details = doc.get("scoreDetails", {})
        details = score_details.get("details", [])
        drove = get_drove_by(score_details)
        text_rank = next((d.get("rank", "NA") for d in details if d.get("inputPipelineName") == "textPipeline"), "NA")
        vector_rank = next((d.get("rank", "NA") for d in details if d.get("inputPipelineName") == "vectorPipeline"), "NA")
        results.append({
            "product_name": doc.get("product_name", "Unknown"),
            "brands": doc.get("brands", ""),
            "nutriscore_grade": doc.get("nutriscore_grade", ""),
            "nova_group": doc.get("nova_group"),
            "categories_tags": doc.get("categories_tags", []),
            "labels_tags": doc.get("labels_tags", []),
            "sodium_100g": doc.get("sodium_100g"),
            "proteins_100g": doc.get("proteins_100g"),
            "sugars_100g": doc.get("sugars_100g"),
            "energy_kcal_100g": doc.get("energy-kcal_100g"),
            "image_url": doc.get("image_url") or doc.get("image_small_url"),
            "score": round(doc.get("score", 0), 4),
            "drove_by": drove,
            "text_rank": text_rank,
            "vector_rank": vector_rank,
        })

    return {
        "results": results,
        "search_stage": search_stage,
        "pipeline": pipeline,
        "reason": reason,
        "constraints": explain_search_stage(search_stage),
        "query": req.query,
    }
