import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_drove_by(score_details: dict) -> str:
    details = score_details.get("details", [])
    def _rank(d):
        v = d.get("rank", 0)
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    contributed = {d["inputPipelineName"] for d in details if _rank(d) > 0}
    if contributed == {"textPipeline", "vectorPipeline"}:
        return "Both"
    elif "textPipeline" in contributed:
        return "Text"
    elif "vectorPipeline" in contributed:
        return "Vector"
    return "Unknown"


def build_rank_fusion_pipeline(
    search_stage: dict,
    query_vector: list,
    text_weight: float,
    vector_weight: float,
    top_k: int,
    inner_limit: int = 20,
) -> list[dict]:
    return [
        {
            "$rankFusion": {
                "input": {
                    "pipelines": {
                        "textPipeline": [
                            {"$search": search_stage},
                            {"$limit": inner_limit}
                        ],
                        "vectorPipeline": [
                            {
                                "$vectorSearch": {
                                    "index": config.INDEX_VECTOR_NAME,
                                    "path": "embedding",
                                    "queryVector": query_vector,
                                    "numCandidates": inner_limit * 10,
                                    "limit": inner_limit
                                }
                            }
                        ]
                    }
                },
                "combination": {
                    "weights": {
                        "textPipeline": text_weight,
                        "vectorPipeline": vector_weight
                    }
                },
                "scoreDetails": True
            }
        },
        {
            "$addFields": {
                "score": {"$meta": "score"},
                "scoreDetails": {"$meta": "scoreDetails"}
            }
        },
        {"$limit": top_k}
    ]
