import pandas as pd

# ── Helpers ──────────────────────────────────────────────────────────────────
def inr(value):
    """Format a float as INR currency string."""
    return f"₹{value:,.2f}"

def divider(char="─", width=62):
    print(char * width)

def section(title):
    divider("═")
    print(f"  {title}")
    divider("═")

# ── 1. Load data ─────────────────────────────────────────────────────────────
df = pd.read_csv("cleaned_sales_data.csv")
df["Date"]   = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
df["Qty"]    = pd.to_numeric(df["Qty"],    errors="coerce").fillna(0).astype(int)
df["B2B"]    = df["B2B"].astype(str).str.strip().str.lower().map(
                   {"true": True, "false": False}).fillna(False)

# ── 2. GTV vs Net Fulfilled Revenue ─────────────────────────────────────────
gtv          = df["Amount"].sum()
fulfilled_df = df[~df["Status"].str.lower().str.contains("cancel", na=False)]
net_revenue  = fulfilled_df["Amount"].sum()
cancelled_df = df[df["Status"].str.lower().str.contains("cancel", na=False)]
cancelled_rev = cancelled_df["Amount"].sum()

# ── 3. Units sold & AOV ──────────────────────────────────────────────────────
total_units  = fulfilled_df["Qty"].sum()
order_count  = fulfilled_df["Order ID"].nunique()
aov          = net_revenue / order_count if order_count else 0

# ── Print ────────────────────────────────────────────────────────────────────
print()
section("AMAZON SALES — EXECUTIVE SUMMARY")
print(f"  {'Total Records':<35} {len(df):>10,}")
print(f"  {'Date Range':<35} {df['Date'].min().date()}  →  {df['Date'].max().date()}")
divider()

# ── Revenue Overview ─────────────────────────────────────────────────────────
print()
section("REVENUE OVERVIEW")
print(f"  {'Gross Transaction Volume (GTV)':<35} {inr(gtv):>15}")
print(f"  {'Cancelled Order Value':<35} {inr(cancelled_rev):>15}")
print(f"  {'Net Fulfilled Revenue':<35} {inr(net_revenue):>15}")
divider()
print(f"  {'Total Units Sold (fulfilled)':<35} {total_units:>15,}")
print(f"  {'Fulfilled Unique Orders':<35} {order_count:>15,}")
print(f"  {'Average Order Value (AOV)':<35} {inr(aov):>15}")
divider()

# ── 4a. Top 5 Categories by Revenue ─────────────────────────────────────────
print()
section("TOP 5 PRODUCT CATEGORIES  (by Net Revenue)")
cat_rev = (fulfilled_df.groupby("Category")["Amount"]
           .sum().sort_values(ascending=False).head(5))
for rank, (cat, rev) in enumerate(cat_rev.items(), 1):
    pct = rev / net_revenue * 100 if net_revenue else 0
    print(f"  {rank}. {cat:<30} {inr(rev):>14}   ({pct:5.1f}%)")
divider()

# ── 4b. Top 5 States by Revenue ──────────────────────────────────────────────
print()
section("TOP 5 SHIPPING STATES  (by Net Revenue)")
state_rev = (fulfilled_df.groupby("ship-state")["Amount"]
             .sum().sort_values(ascending=False).head(5))
for rank, (state, rev) in enumerate(state_rev.items(), 1):
    pct = rev / net_revenue * 100 if net_revenue else 0
    print(f"  {rank}. {state:<30} {inr(rev):>14}   ({pct:5.1f}%)")
divider()

# ── 4c. Fulfilment Channel Distribution ──────────────────────────────────────
print()
section("FULFILMENT CHANNEL DISTRIBUTION")
ful_counts = df["Fulfilment"].value_counts()
ful_total  = ful_counts.sum()
for channel, count in ful_counts.items():
    label = "Amazon Easy Ship" if channel == "Amazon" else "Merchant"
    pct   = count / ful_total * 100
    print(f"  {label:<30} {count:>10,} orders   ({pct:5.1f}%)")
divider()

# ── 4d. Top 5 Order Statuses ─────────────────────────────────────────────────
print()
section("TOP 5 ORDER STATUSES")
status_counts = df["Status"].value_counts().head(5)
for status, count in status_counts.items():
    pct = count / len(df) * 100
    print(f"  {status:<38} {count:>8,}   ({pct:5.1f}%)")
divider()

# ── 4e. B2B vs B2C Average Spend ─────────────────────────────────────────────
print()
section("B2B vs B2C — AVERAGE SPEND PER ORDER")
for label, flag in [("B2B (Business)", True), ("B2C (Consumer)", False)]:
    subset  = fulfilled_df[fulfilled_df["B2B"] == flag]
    n_ord   = subset["Order ID"].nunique()
    avg_rev = subset["Amount"].sum() / n_ord if n_ord else 0
    print(f"  {label:<30} {inr(avg_rev):>14}   ({n_ord:,} orders)")
divider()

print()
print("  Summary generated successfully.")
print()
