import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pymongo
import pymongo.errors
import anthropic
import voyageai
import config
from search.query_expansion import generate_search_stage
from search.pipeline import build_rank_fusion_pipeline
from ui.sidebar import render_sidebar, render_demo_buttons
from ui.results import render_results_grid, render_under_the_hood

st.set_page_config(page_title="MongoDB Structured Search", layout="wide")

@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient(config.MONGODB_URI)

@st.cache_resource
def get_anthropic_client():
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

@st.cache_resource
def get_voyage_client():
    return voyageai.Client(api_key=config.VOYAGE_API_KEY)

@st.cache_resource
def _warmup_claude():
    try:
        generate_search_stage("cereal", get_anthropic_client())
    except Exception:
        pass
    return True

_warmup_claude()


def embed_query_with_client(query: str, voyage_client) -> list:
    result = voyage_client.embed([query], model=config.VOYAGE_MODEL, input_type="query")
    return result.embeddings[0]


@st.cache_data(ttl=300, show_spinner=False)
def cached_search(query: str, text_weight: float, vector_weight: float, top_k: int) -> dict:
    try:
        search_stage, reason = generate_search_stage(query, get_anthropic_client())

        voyage_client = get_voyage_client()
        embed_query_vec = embed_query_with_client(query, voyage_client)

        pipeline = build_rank_fusion_pipeline(
            search_stage, embed_query_vec, text_weight, vector_weight, top_k
        )

        collection = get_mongo_client()[config.MONGODB_DB][config.MONGODB_COLLECTION]
        cursor = collection.aggregate(pipeline)
        return {
            "results": list(cursor),
            "search_stage": search_stage,
            "pipeline": pipeline,
            "reason": reason,
        }
    except voyageai.error.VoyageError:
        st.error("Embedding failed — check VOYAGE_API_KEY in .env")
        return {"results": [], "search_stage": {}, "pipeline": [], "reason": "error"}
    except pymongo.errors.OperationFailure as e:
        errmsg = str(e)
        if "index" in errmsg.lower():
            st.error("Search index still building — wait a moment and retry")
        else:
            st.error(f"Search failed: {errmsg}")
        return {"results": [], "search_stage": {}, "pipeline": [], "reason": "error"}
    except Exception:
        return {"results": [], "search_stage": {}, "pipeline": [], "reason": "error"}


# ---- Main render ----
st.title("MongoDB Structured Search Demo")

text_weight, vector_weight, top_k = render_sidebar()
render_demo_buttons()

col_search, col_btn = st.columns([5, 1])
query = col_search.text_input(
    "Search products...",
    value=st.session_state.get("query", ""),
    key="search_input"
)
search_btn = col_btn.button("Search", use_container_width=True)

if search_btn or (query and query != st.session_state.get("last_query", "")):
    st.session_state["last_query"] = query
    with st.spinner("Searching..."):
        try:
            get_mongo_client().admin.command("ping")
        except pymongo.errors.ConnectionFailure:
            st.error("Atlas connection failed — check MONGODB_URI in .env")
            st.stop()
        result = cached_search(query, text_weight, vector_weight, top_k)
        st.session_state["last_results"] = result

if "last_results" in st.session_state:
    result = st.session_state["last_results"]
    results = result.get("results", [])
    search_stage = result.get("search_stage", {})
    pipeline = result.get("pipeline", [])
    reason = result.get("reason", "ok")

    if reason == "refusal":
        st.warning("Claude couldn't parse that query — using basic text search")

    render_results_grid(results)
    if results:
        render_under_the_hood(search_stage, results, pipeline)
