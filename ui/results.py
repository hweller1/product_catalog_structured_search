import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
from search.pipeline import get_drove_by
from search.explain import explain_search_stage

def render_product_card(col, doc: dict) -> None:
    with col:
        with st.container(border=True):
            # Image with fallback
            img_url = doc.get("image_small_url") or doc.get("image_url")
            if img_url:
                try:
                    st.image(img_url, width=120)
                except Exception:
                    st.image("ui/assets/no_image.png", width=120)
            else:
                st.image("ui/assets/no_image.png", width=120)

            st.markdown(f"**{doc.get('product_name', 'Unknown')}**")
            nutriscore = (doc.get("nutriscore_grade") or "?").upper()
            st.caption(f"{doc.get('brands', '—')} · Nutri-Score: {nutriscore}")
            st.metric("RRF Score", f"{doc.get('score', 0):.2f}")

            # Drove-by badge
            score_details = doc.get("scoreDetails", {})
            drove = get_drove_by(score_details)
            try:
                st.badge(f"Drove by: {drove}")
            except AttributeError:
                st.write(f"Drove by: {drove}")

            # sodium stored in g; display in mg per design.md edge cases
            sodium = doc.get("sodium_100g")
            if sodium is not None:
                st.caption(f"Sodium: {round(sodium * 1000)}mg")


def render_query_routing(search_stage: dict, query: str, reason: str) -> None:
    """Two-column panel showing how Claude and Voyage AI each handled the query."""
    constraints = explain_search_stage(search_stage)

    with st.container(border=True):
        col_text, col_vector = st.columns(2)

        with col_text:
            st.markdown("**🤖 Text pipeline** — Claude → `$search`")
            if constraints:
                for c in constraints:
                    st.markdown(f"- {c}")
            else:
                st.caption("Keyword match on product name")
            if reason in ("refusal", "error", "json_error"):
                st.caption("⚠️ Fallback used — Claude could not parse this query")

        with col_vector:
            st.markdown("**🔍 Vector pipeline** — Voyage AI → `$vectorSearch`")
            st.markdown(f'- Semantic similarity: *"{query}"*')
            st.caption("voyage-4 · 1024-dim embedding · cosine similarity")


def render_results_grid(results: list[dict]) -> None:
    if len(results) == 0:
        st.info("No products found — try broader terms")
        return
    cols = st.columns(3)
    for i, doc in enumerate(results):
        render_product_card(cols[i % 3], doc)


def render_under_the_hood(search_stage: dict, results: list[dict], pipeline: list[dict]) -> None:
    with st.expander("Under the Hood", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Generated $search Query", "Score Breakdown", "Raw Pipeline"])

        with tab1:
            st.json(search_stage)

        with tab2:
            rows = []
            for doc in results:
                details = doc.get("scoreDetails", {}).get("details", [])
                text_rank = next((d.get("rank", 0) for d in details if d.get("inputPipelineName") == "textPipeline"), 0)
                vector_rank = next((d.get("rank", 0) for d in details if d.get("inputPipelineName") == "vectorPipeline"), 0)
                rows.append({
                    "Product": doc.get("product_name", "Unknown"),
                    "RRF Score": round(doc.get("score", 0), 4),
                    "Text Rank": text_rank,
                    "Vector Rank": vector_rank,
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            st.caption("RRF scores are rank-based, not similarity percentages")

        with tab3:
            st.json(pipeline)
