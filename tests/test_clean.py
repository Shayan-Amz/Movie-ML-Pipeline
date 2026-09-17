import pandas as pd
import pytest

from movie_pipeline.clean import clean_movies, genre_columns, one_hot_genres, split_genres, to_number


@pytest.fixture
def raw():
    return pd.DataFrame(
        {
            "year": [1392, 1392, 1393, 1393],
            "title": [" الف ", "ب", "ب", "ج"],
            "genres": ["اجتماعی, درام", "کمدی", "کمدی", None],
            "rating": ["3.3", "10", "10", "4"],
            "viewers": ["15", "1٬200", "1٬200", None],
            "total_sales": ["4,082,605,000", "3٬433٬614٬000", "3٬433٬614٬000", "84000"],
            "mostly_missing": [None, None, None, "x"],
        }
    )


def test_split_genres():
    assert split_genres("اجتماعی, درام ,کمدی") == {"اجتماعی", "درام", "کمدی"}
    assert split_genres(None) == set()
    assert split_genres("") == set()


def test_to_number_strips_persian_and_latin_separators():
    out = to_number(pd.Series(["1٬200", "4,082,605,000", "abc", None]))
    assert out.tolist()[:2] == [1200.0, 4082605000.0]
    assert out.isna().tolist()[2:] == [True, True]


def test_one_hot_genres_is_multilabel():
    df = one_hot_genres(pd.DataFrame({"genres": ["a, b", "b", None]}))
    assert df["genre_a"].tolist() == [1, 0, 0]
    assert df["genre_b"].tolist() == [1, 1, 0]


def test_clean_movies_end_to_end(raw):
    clean = clean_movies(raw)

    # sparse column dropped, duplicates and rating==10 outliers removed
    assert "mostly_missing" not in clean.columns
    assert clean["title"].tolist() == ["الف", "ج"]

    # numeric coercion
    assert clean["rating"].dtype.kind == "f"
    assert clean["total_sales"].tolist() == [4082605000.0, 84000.0]

    # multi-label one-hot encoding
    assert set(genre_columns(clean)) == {"genre_اجتماعی", "genre_درام", "genre_کمدی"}
    assert clean.loc[0, ["genre_اجتماعی", "genre_درام", "genre_کمدی"]].tolist() == [1, 1, 0]
    assert clean.loc[1, ["genre_اجتماعی", "genre_درام", "genre_کمدی"]].tolist() == [0, 0, 0]


def test_clean_movies_does_not_mutate_input(raw):
    snapshot = raw.copy()
    clean_movies(raw)
    pd.testing.assert_frame_equal(raw, snapshot)
