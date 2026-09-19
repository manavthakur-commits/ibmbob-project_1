"""
app.py  —  Supermarket Sales Analytics Dashboard
Run with:  streamlit run app.py
"""

import sys
import os
from pathlib import Path

# ── Make src/ importable ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
import pandas as pd

from data_loader import load_data
from analytics import (
    kpi_summary,
    sales_by_branch,
    sales_by_category,
    sales_by_product,
    sales_by_payment,
    sales_by_gender,
    sales_by_customer_type,
    monthly_sales_trend,
    monthly_category_trend,
    day_of_week_sales,
    rating_by_category,
    rating_distribution,
    branch_category_heatmap,
    gender_category_sales,
    customer_type_category,
    generate_insights,
)
from charts import (
    bar_sales_by_branch,
    bar_sales_by_category,
    pie_sales_by_category,
    pie_payment_methods,
    line_monthly_trend,
    line_monthly_category,
    bar_day_of_week,
    bar_top_products,
    scatter_qty_vs_sales,
    heatmap_branch_category,
    bar_gender_category,
    bar_customer_type,
    bar_rating_by_category,
    hist_rating_distribution,
    box_rating_by_category,
    box_unit_price_by_category,
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Supermarket Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f0f4f8; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] p {
        color: #ffffff !important;
        font-size: 1.55rem !important;
        font-weight: 800 !important;
    }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 16px;
    }

    /* Insight cards */
    .insight-success {
        background: #f0fdf4; border-left: 4px solid #22c55e;
        padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;
    }
    .insight-warning {
        background: #fffbeb; border-left: 4px solid #f59e0b;
        padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;
    }
    .insight-info {
        background: #eff6ff; border-left: 4px solid #3b82f6;
        padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;
    }
    .insight-title { font-weight: 600; font-size: 0.95rem; color: #1e293b; }
    .insight-detail { font-size: 0.87rem; color: #475569; margin-top: 4px; }

    /* Table styling */
    .dataframe th {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .dataframe tr:nth-child(even) { background-color: #f8fafc; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #1e293b; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING  (cached)
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_CSV = Path(__file__).parent.parent / "SUPER MARKET DATA.csv"


@st.cache_data(show_spinner="Loading dataset…")
def get_data(path: str) -> tuple[pd.DataFrame, dict]:
    return load_data(path)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛒 Supermarket Analytics")
    st.markdown("---")

    uploaded = st.file_uploader("📂 Upload CSV (optional)", type=["csv"])

    if uploaded:
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp()) / "data.csv"
        with open(tmp, "wb") as f:
            shutil.copyfileobj(uploaded, f)
        csv_path = str(tmp)
    else:
        csv_path = str(DEFAULT_CSV)

    st.markdown("---")
    st.markdown("### 🔍 Filters")

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    df_raw, dq_report = get_data(csv_path)
except Exception as e:
    st.error(f"**Error loading data:** {e}")
    st.stop()

df = df_raw.copy()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    branches   = st.multiselect("Branch",        sorted(df["Branch"].unique()),   default=sorted(df["Branch"].unique()))
    cities     = st.multiselect("City",          sorted(df["City"].unique()),     default=sorted(df["City"].unique()))
    categories = st.multiselect("Category",      sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
    cust_types = st.multiselect("Customer Type", sorted(df["Customer Type"].unique()), default=sorted(df["Customer Type"].unique()))
    genders    = st.multiselect("Gender",        sorted(df["Gender"].unique()),   default=sorted(df["Gender"].unique()))

    date_min = df["Date"].min().date()
    date_max = df["Date"].max().date()
    date_range = st.date_input("Date Range", value=(date_min, date_max),
                               min_value=date_min, max_value=date_max)

    st.markdown("---")
    st.caption("Supermarket Sales Analytics v1.0")

# ── Apply filters ──────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[(df["Date"] >= start_d) & (df["Date"] <= end_d)]

if branches:   df = df[df["Branch"].isin(branches)]
if cities:     df = df[df["City"].isin(cities)]
if categories: df = df[df["Category"].isin(categories)]
if cust_types: df = df[df["Customer Type"].isin(cust_types)]
if genders:    df = df[df["Gender"].isin(genders)]

if df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your selections.")
    st.stop()

# ── Pre-compute analytics ──────────────────────────────────────────────────────
kpis       = kpi_summary(df)
br_df      = sales_by_branch(df)
cat_df     = sales_by_category(df)
prod_df    = sales_by_product(df)
pay_df     = sales_by_payment(df)
gen_df     = sales_by_gender(df)
ct_df_agg  = sales_by_customer_type(df)
trend_df   = monthly_sales_trend(df)
cat_trend  = monthly_category_trend(df)
dow_df     = day_of_week_sales(df)
rat_df     = rating_by_category(df)
rat_dist   = rating_distribution(df)
hm_pivot   = branch_category_heatmap(df)
gc_df      = gender_category_sales(df)
ctc_df     = customer_type_category(df)
insights   = generate_insights(df, kpis)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 🛒 Supermarket Sales Analytics Dashboard")
st.markdown(
    f"Analysing **{kpis['total_transactions']:,} transactions** across "
    f"**{df['Branch'].nunique()} branches** | "
    f"**{df['City'].nunique()} cities** | "
    f"**{df['Category'].nunique()} categories**"
)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_overview, tab_time, tab_products, tab_customers, tab_ratings, tab_data, tab_quality = st.tabs([
    "📊 Overview",
    "📅 Time Trends",
    "🛍️ Products & Categories",
    "👥 Customer Analysis",
    "⭐ Ratings",
    "📋 Raw Data",
    "🔎 Data Quality",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:

    # ── KPI Metrics ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Total Revenue",      f"₹{kpis['total_revenue']:,.2f}")
    c2.metric("🧾 Transactions",        f"{kpis['total_transactions']:,}")
    c3.metric("🛒 Avg Order Value",     f"₹{kpis['avg_order_value']:,.2f}")
    c4.metric("📦 Units Sold",          f"{int(kpis['total_units_sold']):,}")
    c5.metric("⭐ Avg Rating",          f"{kpis['avg_rating']:.2f} / 5")

    c6, c7, c8, c9, c10 = st.columns(5)
    c6.metric("🏪 Best Branch",         f"Branch {kpis['best_branch']}")
    c7.metric("🏆 Best Category",       kpis['best_category'])
    c8.metric("💳 Top Payment",         kpis['best_payment'])
    c9.metric("🛍️ Unique Products",    str(kpis['unique_products']))
    c10.metric("🧾 Unique Invoices",    f"{kpis['unique_customers']:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Branch & Category charts ───────────────────────────────────────────────
    st.markdown('<div class="section-header">🏪 Branch & Category Performance</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(bar_sales_by_branch(br_df), use_container_width=True, key="ov_branch")
    with col_b:
        st.plotly_chart(pie_sales_by_category(cat_df), use_container_width=True, key="ov_pie_cat")

    col_c, col_d = st.columns(2)
    with col_c:
        st.plotly_chart(bar_sales_by_category(cat_df), use_container_width=True, key="ov_bar_cat")
    with col_d:
        st.plotly_chart(pie_payment_methods(pay_df), use_container_width=True, key="ov_pie_pay")

    # ── Branch Summary Table ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Branch Summary Table</div>', unsafe_allow_html=True)
    display_br = br_df.copy()
    display_br["Total_Sales"]  = display_br["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
    display_br["Avg_Order"]    = display_br["Avg_Order"].apply(lambda x: f"₹{x:,.2f}")
    display_br["Avg_Rating"]   = display_br["Avg_Rating"].apply(lambda x: f"{x:.2f}")
    display_br.columns        = ["Branch", "City", "Total Sales", "Transactions", "Avg Order", "Avg Rating"]
    st.dataframe(display_br, use_container_width=True, hide_index=True)

    # ── Business Insights ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">💡 Business Insights & Recommendations</div>', unsafe_allow_html=True)
    for ins in insights:
        css_class = f"insight-{ins['type']}"
        st.markdown(
            f'<div class="{css_class}">'
            f'<div class="insight-title">{ins["title"]}</div>'
            f'<div class="insight-detail">{ins["detail"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TIME TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab_time:
    st.markdown('<div class="section-header">📅 Sales Over Time</div>', unsafe_allow_html=True)

    st.plotly_chart(line_monthly_trend(trend_df), use_container_width=True, key="tt_monthly")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(bar_day_of_week(dow_df), use_container_width=True, key="tt_dow")
    with col2:
        st.plotly_chart(line_monthly_category(cat_trend), use_container_width=True, key="tt_cat_trend")

    # ── Monthly Summary Table ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Monthly Summary</div>', unsafe_allow_html=True)
    display_trend = trend_df[["Month Label", "Total_Sales", "Transactions", "Avg_Order"]].copy()
    display_trend["Total_Sales"] = display_trend["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
    display_trend["Avg_Order"]   = display_trend["Avg_Order"].apply(lambda x: f"₹{x:,.2f}")
    display_trend.columns = ["Month", "Total Sales", "Transactions", "Avg Order Value"]
    st.dataframe(display_trend, use_container_width=True, hide_index=True)

    # ── Day-of-Week Table ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📆 Day-of-Week Summary</div>', unsafe_allow_html=True)
    display_dow = dow_df.copy()
    display_dow["Total_Sales"] = display_dow["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
    display_dow["Avg_Order"]   = display_dow["Avg_Order"].apply(lambda x: f"₹{x:,.2f}")
    display_dow.columns = ["Day", "Total Sales", "Transactions", "Avg Order Value"]
    st.dataframe(display_dow, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PRODUCTS & CATEGORIES
# ══════════════════════════════════════════════════════════════════════════════
with tab_products:
    st.markdown('<div class="section-header">🛍️ Product & Category Deep Dive</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        top_n = st.slider("Number of top products to show", 5, 30, 15)
        st.plotly_chart(bar_top_products(prod_df, top_n=top_n), use_container_width=True, key="pr_top_products")
    with col2:
        st.plotly_chart(box_unit_price_by_category(df), use_container_width=True, key="pr_unit_price")

    st.plotly_chart(heatmap_branch_category(hm_pivot), use_container_width=True, key="pr_heatmap")

    st.plotly_chart(scatter_qty_vs_sales(df), use_container_width=True, key="pr_scatter")

    # ── Category Summary Table ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Category Summary Table</div>', unsafe_allow_html=True)
    display_cat = cat_df.copy()
    for col in ["Total_Sales", "Avg_Unit_Price"]:
        display_cat[col] = display_cat[col].apply(lambda x: f"₹{x:,.2f}")
    display_cat["Avg_Rating"] = display_cat["Avg_Rating"].apply(lambda x: f"{x:.2f}")
    display_cat.columns = ["Category", "Total Sales", "Total Units", "Transactions", "Avg Unit Price", "Avg Rating"]
    st.dataframe(display_cat, use_container_width=True, hide_index=True)

    # ── Product Table ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🛒 Product Breakdown</div>', unsafe_allow_html=True)
    display_prod = prod_df.copy()
    display_prod["Total_Sales"] = display_prod["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
    display_prod["Avg_Rating"]  = display_prod["Avg_Rating"].apply(lambda x: f"{x:.2f}")
    display_prod.columns = ["Product", "Category", "Total Sales", "Total Units", "Transactions", "Avg Rating"]
    st.dataframe(display_prod, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CUSTOMER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_customers:
    st.markdown('<div class="section-header">👥 Customer Segmentation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(bar_gender_category(gc_df), use_container_width=True, key="cu_gender_cat")
    with col2:
        st.plotly_chart(bar_customer_type(ctc_df), use_container_width=True, key="cu_cust_type")

    col3, col4 = st.columns(2)
    with col3:
        # Gender KPIs
        st.markdown('<div class="section-header">🚻 Gender Summary</div>', unsafe_allow_html=True)
        dg = gen_df.copy()
        dg["Total_Sales"] = dg["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
        dg["Avg_Order"]   = dg["Avg_Order"].apply(lambda x: f"₹{x:,.2f}")
        dg["Avg_Rating"]  = dg["Avg_Rating"].apply(lambda x: f"{x:.2f}")
        dg.columns = ["Gender", "Total Sales", "Transactions", "Avg Order", "Avg Rating"]
        st.dataframe(dg, use_container_width=True, hide_index=True)
    with col4:
        # Customer Type KPIs
        st.markdown('<div class="section-header">🪪 Customer Type Summary</div>', unsafe_allow_html=True)
        dct = ct_df_agg.copy()
        dct["Total_Sales"] = dct["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
        dct["Avg_Order"]   = dct["Avg_Order"].apply(lambda x: f"₹{x:,.2f}")
        dct["Avg_Rating"]  = dct["Avg_Rating"].apply(lambda x: f"{x:.2f}")
        dct.columns = ["Customer Type", "Total Sales", "Transactions", "Avg Order", "Avg Rating"]
        st.dataframe(dct, use_container_width=True, hide_index=True)

    # Payment breakdown
    st.markdown('<div class="section-header">💳 Payment Method Breakdown</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(pie_payment_methods(pay_df), use_container_width=True, key="cu_pie_pay")
    with col6:
        dpay = pay_df.copy()
        dpay["Total_Sales"] = dpay["Total_Sales"].apply(lambda x: f"₹{x:,.2f}")
        dpay["Avg_Order"]   = dpay["Avg_Order"].apply(lambda x: f"₹{x:,.2f}")
        dpay.columns = ["Payment Method", "Total Sales", "Transactions", "Avg Order"]
        st.dataframe(dpay, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — RATINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab_ratings:
    st.markdown('<div class="section-header">⭐ Customer Satisfaction Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(bar_rating_by_category(rat_df), use_container_width=True, key="rt_bar_rating")
    with col2:
        st.plotly_chart(hist_rating_distribution(df), use_container_width=True, key="rt_hist")

    st.plotly_chart(box_rating_by_category(df), use_container_width=True, key="rt_box")

    # Rating table
    st.markdown('<div class="section-header">📋 Rating Statistics by Category</div>', unsafe_allow_html=True)
    drat = rat_df.copy()
    for col in ["Avg_Rating", "Min_Rating", "Max_Rating", "Std_Rating"]:
        drat[col] = drat[col].apply(lambda x: f"{x:.2f}")
    drat.columns = ["Category", "Avg Rating", "Min Rating", "Max Rating", "Std Dev", "Count"]
    st.dataframe(drat, use_container_width=True, hide_index=True)

    # Satisfaction gauge per category
    st.markdown('<div class="section-header">🎯 Satisfaction Score (out of 5)</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(rat_df), 4))
    for i, row in rat_df.iterrows():
        c_idx = i % len(cols)
        pct   = row["Avg_Rating"] / 5 * 100
        color = "#22c55e" if pct >= 75 else ("#f59e0b" if pct >= 55 else "#ef4444")
        cols[c_idx].markdown(
            f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                        padding:14px;text-align:center;margin-bottom:10px;">
                <div style="font-size:0.78rem;color:#64748b;margin-bottom:6px;">{row['Category']}</div>
                <div style="font-size:1.5rem;font-weight:700;color:{color};">{row['Avg_Rating']:.2f}</div>
                <div style="font-size:0.72rem;color:#94a3b8;">{row['Count']} reviews</div>
                <div style="background:#e2e8f0;border-radius:4px;height:6px;margin-top:8px;">
                    <div style="background:{color};width:{pct:.1f}%;height:6px;border-radius:4px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown('<div class="section-header">📋 Filtered Dataset</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", str(df.shape[1]))
    col3.metric("Date Range", f"{df['Date'].min().date()} → {df['Date'].max().date()}")

    search = st.text_input("🔍 Search (Invoice ID / Product / City)", "")
    display_df = df.copy()
    if search:
        mask = (
            display_df["Invoice ID"].str.contains(search, case=False, na=False) |
            display_df["Product"].str.contains(search, case=False, na=False) |
            display_df["City"].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]

    # Format display columns
    show_cols = ["Invoice ID", "Date", "Branch", "City", "Customer Type", "Gender",
                 "Product", "Category", "Quantity", "Unit Price", "Sales", "Payment", "Rating"]
    st.dataframe(
        display_df[show_cols].style.format({
            "Unit Price": "₹{:.2f}",
            "Sales": "₹{:.2f}",
            "Rating": "{:.1f}",
        }),
        use_container_width=True,
        height=450,
    )

    csv_export = display_df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_export,
        file_name="supermarket_filtered.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tab_quality:
    st.markdown('<div class="section-header">🔎 Data Quality Report</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Original Rows",     f"{dq_report['original_rows']:,}")
    c2.metric("Final Rows",        f"{dq_report['final_rows']:,}")
    c3.metric("Duplicates Removed",f"{dq_report['duplicates_removed']:,}")
    c4.metric("Sales Recalculated","✅ Yes" if dq_report["sales_recalculated"] else "❌ No")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Missing Values — Before Cleaning")
        if dq_report["missing_before"]:
            mv_df = pd.DataFrame.from_dict(
                dq_report["missing_before"], orient="index", columns=["Missing Count"]
            ).reset_index().rename(columns={"index": "Column"})
            st.dataframe(mv_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No missing values detected before cleaning.")

    with col2:
        st.markdown("#### Missing Values — After Cleaning")
        if dq_report["missing_after"]:
            mv_after = pd.DataFrame.from_dict(
                dq_report["missing_after"], orient="index", columns=["Missing Count"]
            ).reset_index().rename(columns={"index": "Column"})
            st.dataframe(mv_after, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No missing values remain after cleaning.")

    st.markdown("#### Sales Recalculation Check")
    st.info(
        f"Sales column was **recalculated** as `Quantity × Unit Price` for all rows.  \n"
        f"**{dq_report['sales_mismatch_rows']}** row(s) had a mismatch (>1% tolerance) "
        f"and were corrected."
    )

    st.markdown("#### Dataset Schema")
    schema_data = {
        "Column": df.columns.tolist(),
        "dtype": [str(df[c].dtype) for c in df.columns],
        "Non-Null Count": [df[c].notna().sum() for c in df.columns],
        "Unique Values": [df[c].nunique() for c in df.columns],
        "Sample": [str(df[c].iloc[0]) if len(df) > 0 else "" for c in df.columns],
    }
    st.dataframe(pd.DataFrame(schema_data), use_container_width=True, hide_index=True)

    st.markdown("#### Descriptive Statistics")
    st.dataframe(
        df[["Quantity", "Unit Price", "Sales", "Rating"]].describe().round(2),
        use_container_width=True,
    )
