# 🛒 Supermarket Sales Analytics

A **Streamlit** data analytics dashboard for supermarket sales data. It loads a CSV, cleans and validates it, and presents interactive KPIs, charts, tables, business insights and a data-quality report across seven tabs. All monetary values are displayed in **₹ (INR)**.

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

`app.py` adds `src/` to `sys.path` at startup, so the modules are imported directly (`from data_loader import load_data`) and the app can be launched from any directory.

## Setup & Run

```powershell
# 1. Install dependencies
pip install -r supermarket_analytics/requirements.txt

# 2. Run the dashboard
python -m streamlit run supermarket_analytics/app.py
```

The app opens in wide layout with the sidebar expanded.

## Data Input

The app looks for `SUPER MARKET DATA.csv` **one level above** `supermarket_analytics/` (i.e. in the workspace root).

Alternatively, upload any compatible CSV with **📂 Upload CSV (optional)** in the sidebar. The uploaded file is written to a temporary location and used instead of the default file.

Loading is cached with `st.cache_data`, so the file is only re-processed when the path changes. If loading fails, the error is shown on the page and the app stops.

### Expected columns

The dashboard reads the following columns from the cleaned dataset:

| Column | Used for |
|--------|----------|
| `Invoice ID` | Transaction identifier, searchable in Raw Data |
| `Date` | Date-range filter, monthly and day-of-week trends |
| `Branch`, `City` | Sidebar filters, branch performance |
| `Customer Type`, `Gender` | Sidebar filters, customer segmentation |
| `Product`, `Category` | Sidebar filter (category), product and category analysis |
| `Quantity`, `Unit Price` | Units sold, price distributions, `Sales` recalculation |
| `Sales` | Revenue (recalculated as `Quantity × Unit Price`) |
| `Payment` | Payment-method breakdown |
| `Rating` | Satisfaction analysis |

## Sidebar Controls

All filters apply to **every tab** except the dataset-level counts in the Data Quality tab (see below).

| Control | Description |
|---------|-------------|
| 📂 Upload CSV | Optional. Replaces the default CSV |
| Branch | Multi-select |
| City | Multi-select |
| Category | Multi-select |
| Customer Type | Multi-select |
| Gender | Multi-select |
| Date Range | Start and end date, bounded by the dataset's min/max dates |

All multi-selects start with every value selected. Clearing a multi-select removes that filter rather than emptying the data. If the combined filters match no rows, the app shows a warning and stops rendering until the selection is adjusted.

## Features

The header summarises the filtered data (number of transactions, branches, cities and categories), followed by seven tabs.

| Tab | What it shows |
|-----|--------------|
| 📊 Overview | 10 KPI cards, branch and category charts, branch summary table, business insights |
| 📅 Time Trends | Monthly sales trend, day-of-week analysis, monthly category trend, summary tables |
| 🛍️ Products & Categories | Top-N products, unit-price box plot, branch × category heatmap, quantity vs sales scatter, category and product tables |
| 👥 Customer Analysis | Gender vs category, customer type (member vs normal), gender and customer-type summaries, payment methods |
| ⭐ Ratings | Avg rating by category, rating histogram, box plot, statistics table, satisfaction score cards |
| 📋 Raw Data | Searchable table of the filtered data + CSV download |
| 🔎 Data Quality | Row counts, duplicates, missing values before/after cleaning, Sales recalculation audit, schema, descriptive statistics |

### 📊 Overview

- **KPI cards (two rows of five):** Total Revenue, Transactions, Avg Order Value, Units Sold, Avg Rating, Best Branch, Best Category, Top Payment, Unique Products, Unique Invoices.
- **Charts:** sales by branch (bar), sales by category (pie and bar), payment methods (pie).
- **Branch Summary Table:** branch, city, total sales, transactions, average order, average rating.
- **Business Insights & Recommendations:** auto-generated cards colour-coded by type: success (green), warning (amber) or info (blue).

### 📅 Time Trends

- Monthly sales trend (line), day-of-week sales (bar), monthly trend by category (line).
- **Monthly Summary** table: month, total sales, transactions, average order value.
- **Day-of-Week Summary** table with the same metrics.

### 🛍️ Products & Categories

- **Top products bar chart** with a slider to choose how many products to show (5–30, default 15).
- Unit-price distribution by category (box plot), branch × category sales heatmap, quantity vs sales scatter plot.
- **Category Summary** table: total sales, total units, transactions, average unit price, average rating.
- **Product Breakdown** table: product, category, total sales, total units, transactions, average rating.

### 👥 Customer Analysis

- Gender vs category sales and customer type (member vs normal) charts.
- **Gender Summary** and **Customer Type Summary** tables: total sales, transactions, average order, average rating.
- **Payment Method Breakdown:** pie chart plus a table of total sales, transactions and average order.

### ⭐ Ratings

- Average rating by category (bar), rating distribution (histogram), rating spread by category (box plot).
- **Rating Statistics** table: average, min, max, standard deviation and count per category.
- **Satisfaction Score cards** (one per category, out of 5) with a progress bar, coloured by the score as a percentage of 5:

  | Score | Colour |
  |-------|--------|
  | ≥ 75% (≥ 3.75) | 🟢 Green |
  | ≥ 55% (≥ 2.75) | 🟠 Amber |
  | Below 55% | 🔴 Red |

### 📋 Raw Data

- Metrics for row count, column count and date range of the filtered data.
- **Search box** matching `Invoice ID`, `Product` or `City` (case-insensitive substring).
- Table showing 13 columns: Invoice ID, Date, Branch, City, Customer Type, Gender, Product, Category, Quantity, Unit Price, Sales, Payment, Rating (prices and sales formatted in ₹).
- **⬇️ Download Filtered Data as CSV** exports exactly what is shown (filters and search applied) as `supermarket_filtered.csv`.

### 🔎 Data Quality

- **Metrics:** original rows, final rows, duplicates removed, and whether Sales was recalculated.
- **Missing values** reported per column, before and after cleaning.
- **Sales Recalculation Check:** `Sales` is recalculated as `Quantity × Unit Price` for all rows, and the number of rows whose original value differed by more than 1% is reported.
- **Dataset Schema:** column, dtype, non-null count, unique values, sample value.
- **Descriptive Statistics** for `Quantity`, `Unit Price`, `Sales` and `Rating`.

> **Note:** the row counts, duplicate counts, missing-value tables and recalculation results describe the file as loaded and cleaned, so they are **not** affected by the sidebar filters. The schema table and descriptive statistics use the currently **filtered** data.

## Data Pipeline

1. **Load** — reads the CSV, validates required columns
2. **Clean** — handles missing values, duplicates, bad dates, type coercions
3. **Recalculate** — `Sales = Quantity × Unit Price` (flags any mismatches)
4. **Derive** — adds Month, Day-of-Week, Quarter columns
5. **Filter** — sidebar selections are applied to the cleaned data in `app.py`
6. **Aggregate** — KPIs, group-bys, pivots and insights via `analytics.py`
7. **Visualise** — Plotly charts via `charts.py`, rendered in Streamlit

`load_data(path)` returns the cleaned DataFrame together with a data-quality report (original/final rows, duplicates removed, missing values before/after, Sales recalculation flag and mismatch count), which feeds the Data Quality tab.
