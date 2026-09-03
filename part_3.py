import streamlit as st
import pandas as pd
from pathlib import Path

# =========================================
# Utility functions (exact‑combo recommender)
# =========================================

def load_movies(csv_path: Path) -> pd.DataFrame:
    """Read cleaned CSV with one‑hot genre columns and numeric conversions."""
    df = pd.read_csv(csv_path)
    # Convert numeric columns if present
    for col in ["rating", "total_sales", "viewers"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Detect genre columns (prefix 'genre_')
    genre_cols = [c for c in df.columns if c.startswith("genre_")]
    if not genre_cols:
        raise ValueError("No one‑hot genre columns (genre_*) found in dataset.")
    df["_genre_sig"] = df[genre_cols].astype(int).astype(str).agg("-".join, axis=1)
    return df


def recommend_exact_combo(base_titles: list[str], df: pd.DataFrame, top_k: int = 5):
    """Return two DataFrames (top_k by rating & total_sales) sharing **exact same genre vector**."""
    if len(base_titles) != 3:
        raise ValueError("Select exactly three movies.")

    base_rows = df[df["title"].isin(base_titles)]
    if base_rows.empty:
        raise ValueError("None of the selected titles found in dataset.")

    signatures = base_rows["_genre_sig"].unique().tolist()
    candidates = df[(df["_genre_sig"].isin(signatures)) & (~df["title"].isin(base_titles))]
    if candidates.empty:
        raise ValueError("No movies with the exact same genre combination found.")

    top_rated = candidates.sort_values("rating", ascending=False).head(top_k)
    top_sales = candidates.sort_values("total_sales", ascending=False).head(top_k)
    return top_rated, top_sales

# ==================
# Streamlit Frontend
# ==================

st.set_page_config(page_title="Exact‑Combo Movie Recommender", layout="wide")
st.title("🎬 Exact‑Genre‑Combo Movie Recommender")

DATA_PATH = Path("all_years_movies_cleaned_ohe.csv")
if not DATA_PATH.exists():
    st.error("❌ Dataset 'all_years_movies_cleaned_ohe.csv' not found in app directory.")
    st.stop()

movies_df = load_movies(DATA_PATH)
all_titles = movies_df["title"].dropna().sort_values().unique().tolist()

selected_titles = st.multiselect(
    "Select **exactly three** base movies (search enabled):",
    options=all_titles,
    default=all_titles[:3],
    max_selections=3,
)

if len(selected_titles) == 3:
    if st.button("Recommend"):
        try:
            top_rated, top_sales = recommend_exact_combo(selected_titles, movies_df, top_k=5)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏆 Top 5 by Rating (same combo)")
                st.dataframe(top_rated[["title", "rating"]], hide_index=True)
            with col2:
                st.subheader("💰 Top 5 by Total Sales (same combo)")
                st.dataframe(top_sales[["title", "total_sales"]], hide_index=True)
        except ValueError as e:
            st.error(str(e))
elif len(selected_titles) > 3:
    st.warning("⚠️ Please select only three movies.")
else:
    st.info("Choose three movies to see recommendations.")
