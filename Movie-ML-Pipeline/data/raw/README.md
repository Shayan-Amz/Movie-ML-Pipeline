# Raw data

Place the saved archive pages here, one per Solar Hijri release year:

```
data/raw/1392.html
data/raw/1393.html
…
data/raw/1403.html
```

The source archive is a client-side rendered (Angular) web page, so each file must be
saved from the browser **after** the page has fully rendered (e.g. *Save page as → Web page, complete*
or copying `document.documentElement.outerHTML` from DevTools).

`*.html` files are git-ignored because they are large and site-specific. Run

```bash
python -m movie_pipeline.extract --html-dir data/raw --out data/raw/all_years_movies.csv
```

to produce the raw CSV, then `python -m movie_pipeline.clean` to produce the processed dataset.
