# 🛒 Supermarket Sales Analytics

A **Streamlit** data analytics dashboard for supermarket sales data.

## Project Structure

```
supermarket_analytics/
├── app.py                  # Streamlit dashboard (main entry point)
├── requirements.txt        # Python dependencies
└── src/
    ├── data_loader.py      # CSV loading, cleaning, validation
    ├── analytics.py        # All KPI / aggregation logic
    └── charts.py           # All Plotly chart builders
```

## Setup & Run

```powershell
# 1. Install dependencies
pip install -r supermarket_analytics/requirements.txt

# 2. Run the dashboard
python -m streamlit run 
supermarket_analytics/app.py
```

The app expects `SUPER MARKET DATA.csv` to sit **one level above** `supermarket_analytics/`
(i.e. in the workspace root). You can also upload any compatible CSV directly in the sidebar.

## Features

| Tab | What it shows |
|-----|--------------|
| 📊 Overview | KPI cards, branch/category charts, business insights |
| 📅 Time Trends | Monthly trend, day-of-week analysis, category timeline |
| 🛍️ Products & Categories | Top products, heatmap, scatter plot, unit-price distributions |
| 👥 Customer Analysis | Gender vs category, member vs normal, payment methods |
| ⭐ Ratings | Avg rating by category, histogram, box plot, satisfaction gauges |
| 📋 Raw Data | Searchable, filterable table + CSV download |
| 🔎 Data Quality | Missing values report, Sales recalculation audit, schema info |

## Data Pipeline

1. **Load** — reads CSV, validates required columns  
2. **Clean** — handles missing values, bad dates, type coercions  
3. **Recalculate** — `Sales = Quantity × Unit Price` (flags any mismatches)  
4. **Derive** — adds Month, Day-of-Week, Quarter columns  
5. **Aggregate** — KPIs, group-bys, pivots via `analytics.py`  
6. **Visualise** — Plotly charts via `charts.py`, rendered in Streamlit  
