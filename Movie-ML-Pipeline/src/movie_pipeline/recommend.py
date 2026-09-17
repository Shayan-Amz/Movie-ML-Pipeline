"""Stage 3 — Exact-genre-combination recommender.

Every movie is reduced to a binary *genre signature* — the concatenation of its
``genre_*`` one-hot flags (e.g. ``1-0-0-…-1``). Given a few reference titles, the
recommender returns other movies whose signature is **identical** to one of the
references, ranked two ways:

* by ``rating``       → "critically liked" recommendations
* by ``total_sales``  → "commercially successful" recommendations

This is a deliberately transparent content-based approach: with 43 genres and
686 movies the dataset has only ~100 distinct signatures, so exact matching is
both fast (a single boolean mask) and easy to explain to a user.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from movie_pipeline.clean import GENRE_PREFIX, genre_columns

SIGNATURE_COLUMN = "_genre_sig"
NUMERIC_COLUMNS = ("rating", "total_sales", "viewers")
REQUIRED_BASE_TITLES = 3


def add_genre_signature(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of *df* with a ``_genre_sig`` column built from the ``genre_*`` flags."""
    cols = genre_columns(df)
    if not cols:
        raise ValueError(f"No one-hot genre columns ({GENRE_PREFIX}*) found in dataset.")
    out = df.copy()
    out[SIGNATURE_COLUMN] = out[cols].fillna(0).astype(int).astype(str).agg("-".join, axis=1)
    return out


def load_movies(csv_path: Path | str) -> pd.DataFrame:
    """Read the cleaned CSV, coerce numeric columns and attach the genre signature."""
    df = pd.read_csv(csv_path)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return add_genre_signature(df)


def recommend_exact_combo(
    base_titles: Sequence[str],
    df: pd.DataFrame,
    top_k: int = 5,
    n_required: int = REQUIRED_BASE_TITLES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(top_by_rating, top_by_sales)`` for movies sharing a reference genre signature.

    Parameters
    ----------
    base_titles:
        Exactly *n_required* movie titles the user already likes.
    df:
        A DataFrame produced by :func:`load_movies` / :func:`add_genre_signature`.
    top_k:
        Number of recommendations per ranking.
    """
    if len(base_titles) != n_required:
        raise ValueError(f"Select exactly {n_required} movies.")
    if SIGNATURE_COLUMN not in df.columns:
        df = add_genre_signature(df)

    base_rows = df[df["title"].isin(base_titles)]
    if base_rows.empty:
        raise ValueError("None of the selected titles were found in the dataset.")

    signatures = base_rows[SIGNATURE_COLUMN].unique().tolist()
    candidates = df[df[SIGNATURE_COLUMN].isin(signatures) & ~df["title"].isin(base_titles)]
    if candidates.empty:
        raise ValueError("No other movies share the exact same genre combination.")

    top_rated = candidates.sort_values("rating", ascending=False, na_position="last").head(top_k)
    top_sales = candidates.sort_values("total_sales", ascending=False, na_position="last").head(top_k)
    return top_rated, top_sales
