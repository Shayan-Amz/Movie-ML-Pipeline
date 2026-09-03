# 🎬 Iranian Cinema Analytics & Exact-Genre Movie Recommender

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Web_Scraping-green?style=for-the-badge)](https://www.crummy.com/software/BeautifulSoup/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An end-to-end data science and machine learning pipeline designed to scrape, clean, analyze, and recommend Iranian cinema movies released between **1392 and 1403 (2013 – 2024)**. 

The project features an interactive **Streamlit** dashboard delivering content-based recommendations powered by an **Exact Multi-Genre Combinatorial Matching** algorithm.

---

## 📌 Table of Contents
- [Project Overview](#-project-overview)
- [Pipeline Architecture](#-pipeline-architecture)
- [Dataset Summary](#-dataset-summary)
- [Key Features](#-key-features)
- [Repository Structure](#-repository-structure)
- [Recommendation Engine Logic](#-recommendation-engine-logic)
- [Quickstart & Installation](#-quickstart--installation)
- [Usage Guide](#-usage-guide)
- [Dependencies](#-dependencies)
- [License](#-license)

---

## 🚀 Project Overview

The Iranian film industry produces hundreds of cinematic titles across varied genres every year. This project provides a full-cycle engineering solution to:
1. **Scrape & Extract:** Collect structured box-office archives, audience ratings, cast information, and metadata across 12 consecutive release years.
2. **Clean & Preprocess:** Standardize Persian numerical formats, impute/remove missing values, filter outliers, and apply multi-label one-hot encoding across 40+ genres.
3. **Interactive Recommender System:** Provide a Streamlit web application where users select three reference films to receive tailored recommendations based on exact multi-genre fingerprints, ranked by both critical acclaim (user rating) and commercial success (total sales).

---

## 🔄 Pipeline Architecture

```text
[ HTML Archives (1392-1403) ]
             │
             ▼  (extract.py / BeautifulSoup4)
   [ all_years_movies.csv ]  (Raw Scraped Data)
             │
             ▼  (part_2.ipynb / Pandas)
  ├── Drop sparse columns (>50% null)
  ├── Clean Persian text & currency symbols (٬ ,)
  ├── Multi-label One-Hot Encoding (43 genres)
  └── Outlier filtering (rating != 10)
             │
             ▼
[ all_years_movies_cleaned_ohe.csv ]  (686 movies, 52 features)
             │
             ▼  (part_3.py / Streamlit)
┌─────────────────────────────────────────────────────────────┐
│  Exact-Combo Recommender Dashboard                          │
│  ├── 🏆 Top 5 Recommendations by User Rating (Quality)     │
│  └── 💰 Top 5 Recommendations by Total Sales (Commercial)   │
└─────────────────────────────────────────────────────────────┘
