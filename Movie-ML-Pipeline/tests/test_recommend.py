from pathlib import Path

import pandas as pd
import pytest

from movie_pipeline.recommend import SIGNATURE_COLUMN, add_genre_signature, load_movies, recommend_exact_combo

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed" / "all_years_movies_cleaned_ohe.csv"


@pytest.fixture
def toy():
    df = pd.DataFrame(
        {
            "title": ["A", "B", "C", "D", "E", "F"],
            "rating": [4.5, 3.0, 4.9, 2.0, 3.5, 4.0],
            "total_sales": [10, 500, 20, 900, 5, 100],
            "genre_x": [1, 1, 1, 0, 1, 1],
            "genre_y": [0, 0, 0, 1, 0, 0],
        }
    )
    return add_genre_signature(df)


def test_signature_is_built_from_genre_flags(toy):
    assert toy.loc[0, SIGNATURE_COLUMN] == "1-0"
    assert toy.loc[3, SIGNATURE_COLUMN] == "0-1"


def test_add_genre_signature_requires_genre_columns():
    with pytest.raises(ValueError, match="genre_"):
        add_genre_signature(pd.DataFrame({"title": ["A"]}))


def test_recommendations_share_signature_and_exclude_bases(toy):
    top_rated, top_sales = recommend_exact_combo(["A", "B", "C"], toy, top_k=5)
    # D has a different signature; A, B, C are the bases → only E and F remain
    assert set(top_rated["title"]) == {"E", "F"}
    assert top_rated["title"].tolist() == ["F", "E"]  # 4.0 > 3.5
    assert top_sales["title"].tolist() == ["F", "E"]  # 100 > 5


def test_requires_exactly_three_titles(toy):
    with pytest.raises(ValueError, match="exactly 3"):
        recommend_exact_combo(["A"], toy)


def test_unknown_titles_raise(toy):
    with pytest.raises(ValueError, match="not(?:hing| found)|were found"):
        recommend_exact_combo(["X", "Y", "Z"], toy)


@pytest.mark.skipif(not PROCESSED.exists(), reason="processed dataset not present")
def test_real_dataset_smoke():
    movies = load_movies(PROCESSED)
    assert len(movies) == 686
    assert sum(c.startswith("genre_") for c in movies.columns) == 43
    bases = movies["title"].head(3).tolist()
    top_rated, top_sales = recommend_exact_combo(bases, movies, top_k=5)
    assert 0 < len(top_rated) <= 5 and 0 < len(top_sales) <= 5
    assert not set(top_rated["title"]) & set(bases)
