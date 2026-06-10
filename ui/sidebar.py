"""Sidebar UI controls: weight sliders and top_k select slider."""

import streamlit as st

DEMO_QUERIES = [
    ("Label filter: kosher + low sodium", "kosher low sodium soup"),
    ("Semantic: organic cereal intent", "organic whole grain cereal kids"),
    ("Hybrid: vegan protein bar", "vegan protein bar chocolate"),
    ("Claims: gluten free + high protein", "gluten free pasta high protein"),
    ("Semantic only: keto snack", "keto friendly snack low carb"),
    ("Token exact: Nutri-Score A", "Nutri-Score A dairy product"),
    ("Lexical: brand search", "Clif bar flavors"),
    ("Multi-constraint: high fiber", "high fiber breakfast food low sugar"),
]


def render_demo_buttons() -> None:
    """Render pre-baked demo query buttons in the sidebar."""
    with st.sidebar:
        st.subheader("Demo Queries")
        if st.button("Label filter: kosher + low sodium", use_container_width=True):
            st.session_state["query"] = "kosher low sodium soup"
            st.rerun()
        if st.button("Semantic: organic cereal intent", use_container_width=True):
            st.session_state["query"] = "organic whole grain cereal kids"
            st.rerun()
        if st.button("Hybrid: vegan protein bar", use_container_width=True):
            st.session_state["query"] = "vegan protein bar chocolate"
            st.rerun()
        if st.button("Claims: gluten free + high protein", use_container_width=True):
            st.session_state["query"] = "gluten free pasta high protein"
            st.rerun()
        if st.button("Semantic only: keto snack", use_container_width=True):
            st.session_state["query"] = "keto friendly snack low carb"
            st.rerun()
        if st.button("Token exact: Nutri-Score A", use_container_width=True):
            st.session_state["query"] = "Nutri-Score A dairy product"
            st.rerun()
        if st.button("Lexical: brand search", use_container_width=True):
            st.session_state["query"] = "Clif bar flavors"
            st.rerun()
        if st.button("Multi-constraint: high fiber", use_container_width=True):
            st.session_state["query"] = "high fiber breakfast food low sugar"
            st.rerun()


def render_sidebar() -> tuple[float, float, int]:
    """Render sidebar controls and return (text_weight, vector_weight, top_k)."""
    with st.sidebar:
        st.title("Search Controls")
        text_weight = st.slider(
            "Text Weight", 0.0, 2.0, 1.0, 0.1, key="text_weight"
        )
        vector_weight = st.slider(
            "Vector Weight", 0.0, 2.0, 1.0, 0.1, key="vector_weight"
        )
        top_k = st.select_slider(
            "Results per page", options=[5, 10, 15, 20], value=10, key="top_k"
        )
    return (text_weight, vector_weight, top_k)
