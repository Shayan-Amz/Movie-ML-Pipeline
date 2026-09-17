"""Streamlit front-end for the exact-genre-combination recommender.

Run from the repository root::

    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Make ``src/`` importable when the app is launched without installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from movie_pipeline.recommend import REQUIRED_BASE_TITLES, load_movies, recommend_exact_combo  # noqa: E402

DATA_PATH = ROOT / "data" / "processed" / "all_years_movies_cleaned_ohe.csv"
DISPLAY_COLUMNS = ["title", "year", "director", "genres", "rating", "total_sales"]


@st.cache_data(show_spinner="Loading dataset…")
def _load(path: Path) -> pd.DataFrame:
    return load_movies(path)


st.set_page_config(page_title="Exact-Genre Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Exact-Genre-Combo Movie Recommender")
st.caption(
    "Iranian cinema releases 1392–1403 SH (2013–2024). Pick three movies you like; "
    "you will get other titles with the **exact same genre combination**, ranked by rating and by box-office revenue."
)

if not DATA_PATH.exists():
    st.error(f"Dataset not found: `{DATA_PATH.relative_to(ROOT)}`. Run the extraction and cleaning stages first.")
    st.stop()

movies = _load(DATA_PATH)
titles = movies["title"].dropna().sort_values().unique().tolist()

with st.sidebar:
    st.header("Dataset")
    st.metric("Movies", f"{len(movies):,}")
    st.metric("Genres", sum(c.startswith("genre_") for c in movies.columns))
    st.metric("Years", f"{int(movies['year'].min())}–{int(movies['year'].max())}")
    top_k = st.slider("Recommendations per list", min_value=3, max_value=10, value=5)

selected = st.multiselect(
    f"Select **exactly {REQUIRED_BASE_TITLES}** movies (type to search):",
    options=titles,
    max_selections=REQUIRED_BASE_TITLES,
)

if len(selected) < REQUIRED_BASE_TITLES:
    st.info(f"Choose {REQUIRED_BASE_TITLES - len(selected)} more movie(s) to get recommendations.")
    st.stop()

if st.button("Recommend", type="primary"):
    try:
        top_rated, top_sales = recommend_exact_combo(selected, movies, top_k=top_k)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    col_rating, col_sales = st.columns(2)
    with col_rating:
        st.subheader("🏆 Top by user rating")
        st.dataframe(top_rated[DISPLAY_COLUMNS], hide_index=True, use_container_width=True)
    with col_sales:
        st.subheader("💰 Top by total sales")
        st.dataframe(
            top_sales[DISPLAY_COLUMNS],
            hide_index=True,
            use_container_width=True,
            column_config={"total_sales": st.column_config.NumberColumn("total_sales (IRR)", format="%d")},
        )
