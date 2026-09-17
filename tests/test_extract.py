from movie_pipeline.extract import extract_all_years, parse_archive_html

SAMPLE_HTML = """
<div class="ng-star-inserted">
  <app-movie-box-archive-desktop>
    <div class="plate">
      <h2 class="title"> فیلم نمونه </h2>
      <div class="director"><span>کارگردان نمونه</span></div>
      <div class="genres"><span>اجتماعی</span><span>درام</span></div>
      <div class="rateBox"><span class="rate">4.2</span></div>
      <div class="rateCountBox"><span class="text">21</span></div>
      <div class="titleTextBox">
        <span class="title">تهیه کننده:</span>
        <span class="value"><span class="ng-star-inserted">تهیه‌کننده نمونه</span></span>
      </div>
      <div class="titleTextBox">
        <span class="title">کل فروش:</span>
        <span class="value">3٬433٬614٬000</span>
      </div>
      <div class="actorPlate"><h4 class="name">بازیگر یک</h4></div>
      <div class="actorPlate"><h4 class="name">بازیگر دو</h4></div>
    </div>
  </app-movie-box-archive-desktop>
</div>
<div class="ng-star-inserted">
  <app-movie-box-archive-desktop><!-- card without a plate is ignored --></app-movie-box-archive-desktop>
</div>
"""


def test_parse_archive_html_extracts_all_fields():
    records = parse_archive_html(SAMPLE_HTML, year=1392)
    assert len(records) == 1
    rec = records[0]
    assert rec["year"] == 1392
    assert rec["title"] == "فیلم نمونه"
    assert rec["director"] == "کارگردان نمونه"
    assert rec["genres"] == "اجتماعی, درام"
    assert rec["rating"] == "4.2"
    assert rec["viewers"] == "21"
    assert rec["producer"] == "تهیه‌کننده نمونه"
    assert rec["total_sales"] == "3٬433٬614٬000"
    assert rec["actors"] == "بازیگر یک, بازیگر دو"


def test_missing_fields_become_empty_strings():
    html = (
        '<div class="ng-star-inserted"><app-movie-box-archive-desktop>'
        '<div class="plate"><h2 class="title">x</h2></div>'
        "</app-movie-box-archive-desktop></div>"
    )
    (rec,) = parse_archive_html(html, year=1400)
    assert rec["title"] == "x"
    assert rec["director"] == rec["producer"] == rec["total_sales"] == rec["actors"] == ""


def test_extract_all_years_skips_missing_files(tmp_path):
    (tmp_path / "1392.html").write_text(SAMPLE_HTML, encoding="utf-8")
    df = extract_all_years(tmp_path, years=[1392, 1393])
    assert list(df["year"]) == [1392]
    assert list(df.columns) == [
        "year", "title", "director", "genres", "rating", "viewers", "producer", "total_sales", "actors",
    ]
