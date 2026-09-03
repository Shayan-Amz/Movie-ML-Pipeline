import pandas as pd
from bs4 import BeautifulSoup
import os

START_YEAR = 1392
END_YEAR = 1403
OUTPUT_CSV = "all_years_movies.csv"

all_data = []

for year in range(START_YEAR, END_YEAR + 1):
    file_path = f"{year}.html"
    if not os.path.exists(file_path):
        print(f"⚠️ فایل «{file_path}» پیدا نشد، نادیده گرفته شد.")
        continue

    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards = soup.select('div.ng-star-inserted > app-movie-box-archive-desktop')

    for card_wrapper in cards:
        plate_div = card_wrapper.select_one('div.plate')
        if not plate_div:
            continue

        title_elem = plate_div.select_one('h2.title')
        title = title_elem.get_text(strip=True) if title_elem else ''

        director_elem = plate_div.select_one('div.director span')
        director = director_elem.get_text(strip=True) if director_elem else ''

        genre_spans = plate_div.select('div.genres span')
        genres = ', '.join(span.get_text(strip=True) for span in genre_spans) if genre_spans else ''

        rate_elem = plate_div.select_one('div.rateBox span.rate')
        rating = rate_elem.get_text(strip=True) if rate_elem else ''

        viewers_elem = plate_div.select_one('div.rateCountBox span.text')
        viewers = viewers_elem.get_text(strip=True) if viewers_elem else ''

        producer = ''
        for textbox in plate_div.select('div.titleTextBox'):
            label_span = textbox.select_one('span.title')
            if label_span and 'تهیه کننده' in label_span.get_text():
                val_span = textbox.select_one('span.value span.ng-star-inserted')
                producer = val_span.get_text(strip=True) if val_span else ''
                break

        total_sales = ''
        for textbox in plate_div.select('div.titleTextBox'):
            label_span = textbox.select_one('span.title')
            if label_span and 'کل فروش' in label_span.get_text():
                val_span = textbox.select_one('span.value')
                total_sales = val_span.get_text(strip=True) if val_span else ''
                break

        actors_list = []
        actor_name_elems = plate_div.select('div.actorPlate h4.name')
        for hn in actor_name_elems:
            name = hn.get_text(strip=True)
            if name:
                actors_list.append(name)
        actors = ', '.join(actors_list)

        all_data.append({
            'year': year,
            'title': title,
            'director': director,
            'genres': genres,
            'rating': rating,
            'viewers': viewers,
            'producer': producer,
            'total_sales': total_sales,
            'actors': actors
        })

df = pd.DataFrame(all_data)
df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"✅ استخراج اطلاعات از فایل‌های {START_YEAR}.html تا {END_YEAR}.html انجام شد.")
print(f"   تعداد کل رکوردها: {len(df)}")
print(f"   نتایج در فایل «{OUTPUT_CSV}» ذخیره شد.")
