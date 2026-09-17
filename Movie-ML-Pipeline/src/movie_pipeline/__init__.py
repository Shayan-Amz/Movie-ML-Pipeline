"""Movie ML Pipeline — scrape, clean and recommend Iranian cinema releases (1392–1403 SH / 2013–2024).

Stages
------
- :mod:`movie_pipeline.extract`   — parse saved box-office archive HTML pages into a tidy table
- :mod:`movie_pipeline.clean`     — clean the raw table and one-hot encode the multi-label genre column
- :mod:`movie_pipeline.recommend` — exact-genre-combination recommender used by the Streamlit app

Each stage is importable (``from movie_pipeline.clean import clean_movies``) and runnable as a
script (``python -m movie_pipeline.clean --help``).
"""

__version__ = "1.0.0"
