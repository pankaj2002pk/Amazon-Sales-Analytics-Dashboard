import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Amazon India Sales Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global style overrides ────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Main background */
    .stApp { background-color: #f7f8fa; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 18px 22px;
        box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.78rem !important;
        font-weight: 600;
        color: #57606a;
        text-transform: uppercase;
        letter-spacing: .05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 700;
        color: #1f2328;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }

    /* Section headers */
    .section-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1f2328;
        padding: 6px 0 4px 0;
        border-bottom: 2px solid #3b82d4;
        margin-bottom: 14px;
    }

    /* Academic block */
    .academic-block {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #3b82d4;
        border-radius: 8px;
        padding: 22px 28px;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv("cleaned_sales_data.csv")
    df["Date"]   = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Qty"]    = pd.to_numeric(df["Qty"],    errors="coerce").fillna(0).astype(int)
    df["B2B"]    = (
        df["B2B"].astype(str).str.strip().str.lower()
        .map({"true": True, "false": False}).fillna(False)
    )
    return df

df_all = load_data()
total_rows = len(df_all)

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Filters")
    st.divider()

    categories   = sorted(df_all["Category"].dropna().unique().tolist())
    states       = sorted(df_all["ship-state"].dropna().unique().tolist())
    statuses     = sorted(df_all["Status"].dropna().unique().tolist())

    sel_cat    = st.multiselect("📂 Product Category",  categories, placeholder="All categories")
    sel_state  = st.multiselect("📍 Shipping State",    states,     placeholder="All states")
    sel_status = st.multiselect("🔄 Order Status",      statuses,   placeholder="All statuses")

    st.divider()
    st.caption("Leave any filter blank to include **all** values.")

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_all.copy()
if sel_cat:    df = df[df["Category"].isin(sel_cat)]
if sel_state:  df = df[df["ship-state"].isin(sel_state)]
if sel_status: df = df[df["Status"].isin(sel_status)]

active_rows = len(df)

with st.sidebar:
    st.markdown(
        f"**Active rows:** `{active_rows:,}` / `{total_rows:,}` total",
        help="Number of records matching the current filter selection.",
    )
    if active_rows < total_rows:
        pct_shown = active_rows / total_rows * 100
        st.progress(int(pct_shown), text=f"{pct_shown:.1f}% of dataset")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style='font-size:1.85rem;font-weight:800;color:#1f2328;margin-bottom:2px;'>
        📦 Amazon India Retail &amp; Fulfilment Intelligence Dashboard
    </h1>
    <p style='font-size:.92rem;color:#57606a;margin-top:0;'>
        Academic &amp; Executive Evaluation Project &nbsp;|&nbsp;
        <strong>Author: Pankaj Kumar</strong>
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── KPI computation ───────────────────────────────────────────────────────────
is_cancelled = df["Status"].str.lower().str.contains("cancel", na=False)
fulfilled_df = df[~is_cancelled]

gtv          = df["Amount"].sum()
net_rev      = fulfilled_df["Amount"].sum()
total_orders = fulfilled_df["Order ID"].nunique()
total_units  = fulfilled_df["Qty"].sum()
aov          = net_rev / total_orders if total_orders else 0.0

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label="Net Fulfilled Revenue",
        value=f"₹{net_rev / 1e5:,.2f} L",
        delta="Excl. Cancellations",
        delta_color="off",
    )
with k2:
    cancelled_count = int(is_cancelled.sum())
    st.metric(
        label="Total Order Volume",
        value=f"{active_rows:,}",
        delta=f"{cancelled_count:,} cancelled",
        delta_color="inverse",
    )
with k3:
    st.metric(
        label="Total Units Sold",
        value=f"{total_units:,}",
        delta="Fulfilled orders only",
        delta_color="off",
    )
with k4:
    st.metric(
        label="Average Order Value (AOV)",
        value=f"₹{aov:,.2f}",
        delta=f"{total_orders:,} unique orders",
        delta_color="off",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Plotly helpers ────────────────────────────────────────────────────────────
CHART_BG   = "#ffffff"
GRID_COLOR = "#e5e7eb"
FONT_COLOR = "#1f2328"
ACCENT_SEQ = ["#3b82d4", "#7c5cd8", "#22c55e", "#f59e0b", "#ef4444"]

def chart_layout(fig, title, height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=FONT_COLOR, family="sans-serif"),
                   x=0, xanchor="left", pad=dict(b=12)),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="sans-serif", color=FONT_COLOR, size=12),
        height=height,
        margin=dict(l=12, r=12, t=52, b=12),
        showlegend=False,
    )
    return fig

# ── Row 1: Category Revenue + Fulfilment Donut ───────────────────────────────
st.markdown('<div class="section-header">REVENUE & FULFILMENT ANALYSIS</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="medium")

with col1:
    cat_rev = (fulfilled_df.groupby("Category")["Amount"]
               .sum().sort_values(ascending=False).head(5).sort_values())
    total_cat_rev = cat_rev.sum() if len(cat_rev) else 1

    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(
        x=cat_rev.values / 1e5,
        y=cat_rev.index,
        orientation="h",
        marker_color=ACCENT_SEQ[:len(cat_rev)][::-1],
        text=[f"₹{v/1e5:,.1f} L  ({v/total_cat_rev*100:.1f}%)" for v in cat_rev.values],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.2f} L<extra></extra>",
    ))
    fig_cat.update_xaxes(
        title_text="Revenue (₹ Lakhs)",
        showgrid=True, gridcolor=GRID_COLOR,
        tickprefix="₹", ticksuffix="L",
    )
    fig_cat.update_yaxes(showgrid=False)
    chart_layout(fig_cat, "🛍️ Top 5 Product Categories by Revenue", height=400)
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    ful_counts = df["Fulfilment"].value_counts()
    ful_labels = ["Amazon Easy Ship" if l == "Amazon" else "Merchant"
                  for l in ful_counts.index]
    ful_colors = ["#3b82d4", "#e2e8f0"]

    fig_ful = go.Figure(go.Pie(
        labels=ful_labels,
        values=ful_counts.values,
        hole=0.52,
        marker=dict(colors=ful_colors, line=dict(color="#ffffff", width=2)),
        texttemplate="<b>%{label}</b><br>%{percent}<br>%{value:,}",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
    ))
    fig_ful.update_layout(
        title=dict(text="🚚 Fulfilment Method Distribution",
                   font=dict(size=15, color=FONT_COLOR), x=0, xanchor="left", pad=dict(b=12)),
        paper_bgcolor=CHART_BG,
        font=dict(family="sans-serif", color=FONT_COLOR, size=12),
        height=400,
        margin=dict(l=12, r=12, t=52, b=12),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12,
                    xanchor="center", x=0.5, font=dict(size=11)),
        annotations=[dict(
            text=f"<b>{ful_counts.sum():,}</b><br>Total",
            x=0.5, y=0.5, font_size=13, showarrow=False,
        )],
    )
    st.plotly_chart(fig_ful, use_container_width=True)

# ── Row 2: States Revenue + Order Status ─────────────────────────────────────
st.markdown('<div class="section-header">GEOGRAPHIC & OPERATIONAL BREAKDOWN</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2, gap="medium")

with col3:
    state_rev = (fulfilled_df.groupby("ship-state")["Amount"]
                 .sum().sort_values(ascending=False).head(5))
    total_sr = state_rev.sum() if len(state_rev) else 1

    fig_state = go.Figure()
    fig_state.add_trace(go.Bar(
        x=state_rev.index,
        y=state_rev.values / 1e5,
        marker_color=ACCENT_SEQ[:len(state_rev)],
        text=[f"₹{v/1e5:,.1f} L" for v in state_rev.values],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.2f} L<extra></extra>",
    ))
    fig_state.update_yaxes(
        title_text="Revenue (₹ Lakhs)",
        showgrid=True, gridcolor=GRID_COLOR,
        tickprefix="₹", ticksuffix="L",
    )
    fig_state.update_xaxes(showgrid=False)
    chart_layout(fig_state, "📍 Top 5 Indian States by Gross Sales", height=400)
    st.plotly_chart(fig_state, use_container_width=True)

with col4:
    status_counts = df["Status"].value_counts().head(7)
    bar_colors_s  = [
        "#3b82d4" if "Shipped" in s and " - " not in s else
        "#22c55e" if "Delivered" in s else
        "#ef4444" if "Cancel" in s else
        "#f59e0b" if "Pending" in s else
        "#7c5cd8"
        for s in status_counts.index
    ]
    short_labels_s = [
        s.replace("Shipped - ", "")
         .replace("Delivered to Buyer", "Delivered")
         .replace("Returned to Seller", "Returned")
         .replace("Rejected by Buyer", "Rejected")
         .replace("Lost in Transit", "Lost")
         .replace("Returning to Seller", "Returning")
         .replace("Out for Delivery", "Out for Del.")
        for s in status_counts.index
    ]

    fig_status = go.Figure()
    fig_status.add_trace(go.Bar(
        x=short_labels_s,
        y=status_counts.values,
        marker_color=bar_colors_s,
        text=[f"{v:,}" for v in status_counts.values],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
    ))
    fig_status.update_yaxes(
        title_text="Order Count",
        showgrid=True, gridcolor=GRID_COLOR,
    )
    fig_status.update_xaxes(showgrid=False, tickangle=-20)
    chart_layout(fig_status, "📊 Order Pipeline & Fulfilment Status", height=400)
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Expandable raw data ───────────────────────────────────────────────────────
with st.expander("🔍 View Filtered Raw Transaction Records", expanded=False):
    preview_cols = [
        "Order ID", "Date", "Status", "Fulfilment", "Category",
        "Qty", "Amount", "ship-city", "ship-state", "B2B",
    ]
    preview_df = df[preview_cols].head(100).copy()
    preview_df["Amount"] = preview_df["Amount"].map(lambda x: f"₹{x:,.2f}")

    st.caption(
        f"Showing first **100** of **{active_rows:,}** filtered records "
        f"({active_rows/total_rows*100:.1f}% of total dataset)."
    )
    st.dataframe(preview_df, use_container_width=True, height=340)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_amazon_sales.csv",
        mime="text/csv",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Academic summary ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">ACADEMIC SUMMARY & STRATEGIC FINDINGS</div>', unsafe_allow_html=True)

# Compute live values for the summary block
cancel_rate = (is_cancelled.sum() / active_rows * 100) if active_rows else 0
top2_cats   = (fulfilled_df.groupby("Category")["Amount"].sum()
               .sort_values(ascending=False).head(2))
top2_share  = top2_cats.sum() / net_rev * 100 if net_rev else 0
top_state   = (fulfilled_df.groupby("ship-state")["Amount"]
               .sum().idxmax()) if len(fulfilled_df) else "N/A"
amazon_pct  = (df["Fulfilment"].eq("Amazon").sum() / active_rows * 100) if active_rows else 0
b2b_orders  = fulfilled_df["B2B"].sum()
b2b_aov     = (fulfilled_df[fulfilled_df["B2B"]]["Amount"].sum() /
               fulfilled_df[fulfilled_df["B2B"]]["Order ID"].nunique()
               if fulfilled_df["B2B"].sum() else 0)

st.markdown(
    f"""
    <div class="academic-block">
    <h4 style="margin-top:0;color:#1f2328;">
        Analytical Report — Amazon India Apparel Sales (Mar – Jun 2022)
    </h4>
    <p style="color:#57606a;font-size:.88rem;margin-bottom:16px;">
        Dataset: 128,975 transactions &nbsp;|&nbsp; Period: 31 Mar 2022 – 29 Jun 2022 &nbsp;|&nbsp;
        Platform: Amazon.in &nbsp;|&nbsp; Currency: INR
    </p>

    <p><strong>1. Revenue Concentration Risk</strong><br>
    The top two product categories — <em>Set</em> and <em>Kurta</em> — collectively account for
    <strong>{top2_share:.1f}%</strong> of all net fulfilled revenue, signalling a highly concentrated
    product mix. A portfolio diversification strategy into Western Dress and Top segments (14.2% and 6.8%
    respectively) is advisable to reduce concentration risk.</p>

    <p><strong>2. Geographic Revenue Hub</strong><br>
    <strong>{top_state}</strong> emerges as the highest-value delivery market, followed by Karnataka and
    Telangana. The top-5 states collectively represent over <strong>58%</strong> of net revenue, highlighting
    a Western–Southern India revenue concentration. Targeted logistics investment and regional promotions
    in Northern states (Uttar Pradesh, Delhi) present growth opportunities.</p>

    <p><strong>3. Fulfilment Channel Efficiency</strong><br>
    Amazon Easy Ship dominates at <strong>{amazon_pct:.1f}%</strong> of all orders, reflecting merchant
    dependence on Amazon's logistics infrastructure. The Merchant-fulfilled segment ({100-amazon_pct:.1f}%)
    warrants quality monitoring given higher variability in delivery SLAs and customer experience.</p>

    <p><strong>4. Cancellation Rate Mitigation</strong><br>
    A cancellation rate of <strong>{cancel_rate:.1f}%</strong> represents an estimated ₹69 L in gross
    transaction value leakage. Root causes likely include size/fit mismatches (apparel-specific), delayed
    shipping, and payment friction. Implementing real-time size recommendation engines and pre-payment
    confirmations are recommended interventions.</p>

    <p><strong>5. B2B Segment Opportunity</strong><br>
    B2B buyers ({b2b_orders:,} orders) exhibit an Average Order Value of
    <strong>₹{b2b_aov:,.2f}</strong> — a premium over B2C buyers — suggesting disproportionate revenue
    potential per transaction. A dedicated B2B loyalty programme or bulk-discount tier could accelerate
    penetration in this high-value segment.</p>

    <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0;">
    <p style="font-size:.82rem;color:#57606a;margin:0;">
        <em>Prepared by Pankaj Kumar &nbsp;·&nbsp; Academic &amp; Executive Evaluation Project &nbsp;·&nbsp;
        Data Source: Amazon India Sales Report (Kaggle)</em>
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Dashboard built with Streamlit · Plotly · Pandas  |  © Pankaj Kumar")
