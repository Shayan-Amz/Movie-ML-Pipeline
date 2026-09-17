"""Stage 1 — Extraction.

Parses locally saved HTML pages of an Iranian box-office archive (one page per
Solar Hijri release year, e.g. ``1392.html`` … ``1403.html``) and turns every
movie card into a flat record.

The archive is an Angular single-page application, so the pages were saved
from the browser *after* they finished rendering; the CSS selectors below
therefore target the rendered DOM (``app-movie-box-archive-desktop`` cards).

Run as a script::

    python -m movie_pipeline.extract --html-dir data/raw --out data/raw/all_years_movies.csv
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup, Tag

log = logging.getLogger(__name__)

START_YEAR = 1392  # 2013-14
END_YEAR = 1403  # 2024-25

CARD_SELECTOR = "div.ng-star-inserted > app-movie-box-archive-desktop"
FIELD_LABELS = {
    "producer": "تهیه کننده",  # "producer"
    "total_sales": "کل فروش",  # "total sales"
}
COLUMNS = [
    "year",
    "title",
    "director",
    "genres",
    "rating",
    "viewers",
    "producer",
    "total_sales",
    "actors",
]


def _text(node: Tag | None) -> str:
    """Return stripped text of a node, or an empty string when the node is missing."""
    return node.get_text(strip=True) if node is not None else ""


def _labelled_value(plate: Tag, label: str, value_selector: str) -> str:
    """Find the ``div.titleTextBox`` whose label contains *label* and return its value text."""
    for textbox in plate.select("div.titleTextBox"):
        label_span = textbox.select_one("span.title")
        if label_span and label in label_span.get_text():
            return _text(textbox.select_one(value_selector))
    return ""


def parse_movie_card(plate: Tag, year: int) -> dict[str, object]:
    """Convert a single rendered movie card (``div.plate``) into a record."""
    actors = [_text(h) for h in plate.select("div.actorPlate h4.name")]
    return {
        "year": year,
        "title": _text(plate.select_one("h2.title")),
        "director": _text(plate.select_one("div.director span")),
        "genres": ", ".join(_text(s) for s in plate.select("div.genres span")),
        "rating": _text(plate.select_one("div.rateBox span.rate")),
        "viewers": _text(plate.select_one("div.rateCountBox span.text")),
        "producer": _labelled_value(
            plate, FIELD_LABELS["producer"], "span.value span.ng-star-inserted"
        ),
        "total_sales": _labelled_value(plate, FIELD_LABELS["total_sales"], "span.value"),
        "actors": ", ".join(a for a in actors if a),
    }


def parse_archive_html(html: str, year: int) -> list[dict[str, object]]:
    """Parse one saved archive page and return a list of movie records."""
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, object]] = []
    for card in soup.select(CARD_SELECTOR):
        plate = card.select_one("div.plate")
        if plate is None:
            continue
        records.append(parse_movie_card(plate, year))
    return records


def extract_all_years(
    html_dir: Path | str,
    years: Iterable[int] = range(START_YEAR, END_YEAR + 1),
) -> pd.DataFrame:
    """Parse ``<year>.html`` for every requested year found in *html_dir*.

    Missing files are skipped with a warning so a partial archive still yields a table.
    """
    html_dir = Path(html_dir)
    records: list[dict[str, object]] = []
    for year in years:
        path = html_dir / f"{year}.html"
        if not path.exists():
            log.warning("Skipping %s — file not found", path)
            continue
        year_records = parse_archive_html(path.read_text(encoding="utf-8"), year)
        log.info("%s: %d movies", path.name, len(year_records))
        records.extend(year_records)
    return pd.DataFrame(records, columns=COLUMNS)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--html-dir", type=Path, default=Path("data/raw"), help="directory holding <year>.html files")
    parser.add_argument("--out", type=Path, default=Path("data/raw/all_years_movies.csv"), help="output CSV path")
    parser.add_argument("--start-year", type=int, default=START_YEAR)
    parser.add_argument("--end-year", type=int, default=END_YEAR)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    df = extract_all_years(args.html_dir, range(args.start_year, args.end_year + 1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False, encoding="utf-8-sig")
    log.info("Extracted %d records from %d–%d → %s", len(df), args.start_year, args.end_year, args.out)


if __name__ == "__main__":
    main()
