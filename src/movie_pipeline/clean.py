"""Stage 2 — Cleaning & feature engineering.

Reproduces the steps of ``notebooks/02_data_cleaning.ipynb`` as a pure function so
they can be unit-tested and re-run from the command line:

1. drop columns that are more than 50 % missing;
2. strip whitespace from every text column;
3. convert ``rating`` / ``viewers`` / ``total_sales`` to numbers (Persian thousands
   separators ``٬`` and commas are removed first);
4. drop exact duplicate rows;
5. multi-label one-hot encode the comma-separated ``genres`` column into ``genre_*`` flags;
6. remove the rating-outlier rows (a rating of exactly 10 on a 5-point scale is a
   data-entry artefact of the source archive).

Run as a script::

    python -m movie_pipeline.clean --inp data/raw/all_years_movies.csv \\
        --out data/processed/all_years_movies_cleaned_ohe.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

GENRE_PREFIX = "genre_"
NUMERIC_COLUMNS = ("rating", "viewers", "total_sales")
MISSING_THRESHOLD = 0.50
RATING_OUTLIER = 10
_THOUSANDS_SEPARATORS = r"[٬, ]"


def split_genres(value: object) -> set[str]:
    """``"اجتماعی, درام, کمدی"`` → ``{"اجتماعی", "درام", "کمدی"}`` (empty set for NaN)."""
    if pd.isna(value):
        return set()
    return {g.strip() for g in str(value).split(",") if g.strip()}


def to_number(series: pd.Series) -> pd.Series:
    """Strip Persian/Latin thousands separators and coerce to float (unparseable → NaN)."""
    cleaned = series.astype("string").str.replace(_THOUSANDS_SEPARATORS, "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def one_hot_genres(df: pd.DataFrame, column: str = "genres") -> pd.DataFrame:
    """Append one ``genre_<name>`` indicator column per distinct genre (multi-label)."""
    genre_sets = df[column].map(split_genres)
    unique_genres = sorted({g for s in genre_sets for g in s})
    flags = pd.DataFrame(
        {f"{GENRE_PREFIX}{g}": genre_sets.map(lambda s, g=g: int(g in s)) for g in unique_genres},
        index=df.index,
    )
    return pd.concat([df, flags], axis=1)


def clean_movies(raw: pd.DataFrame) -> pd.DataFrame:
    """Apply the full cleaning pipeline and return a new DataFrame."""
    df = raw.copy()

    missing_ratio = df.isna().mean()
    dropped = missing_ratio[missing_ratio > MISSING_THRESHOLD].index.tolist()
    if dropped:
        log.info("Dropping sparse columns (> %.0f%% missing): %s", MISSING_THRESHOLD * 100, dropped)
        df = df.drop(columns=dropped)

    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].str.strip()

    for col in NUMERIC_COLUMNS:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = to_number(df[col])

    df = df.drop_duplicates()

    if "genres" in df.columns:
        df = one_hot_genres(df)

    if "rating" in df.columns:
        before = len(df)
        df = df[df["rating"] != RATING_OUTLIER]
        log.info("Removed %d rating-outlier rows", before - len(df))

    return df.reset_index(drop=True)


def genre_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of one-hot genre columns present in *df*."""
    return [c for c in df.columns if c.startswith(GENRE_PREFIX)]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inp", type=Path, default=Path("data/raw/all_years_movies.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/all_years_movies_cleaned_ohe.csv"))
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raw = pd.read_csv(args.inp)
    clean = clean_movies(raw)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.out, index=False, encoding="utf-8-sig")
    log.info(
        "Cleaned %d → %d rows, %d columns (%d genre flags) → %s",
        len(raw), len(clean), clean.shape[1], len(genre_columns(clean)), args.out,
    )


if __name__ == "__main__":
    main()
