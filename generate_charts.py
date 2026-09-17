import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Setup ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = "project_charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

DPI        = 300
ACCENT     = "#3b82d4"          # primary blue
PALETTE_6  = ["#3b82d4", "#7c5cd8", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4"]
BG         = "#ffffff"
MUTED      = "#57606a"

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.edgecolor":   "#e5e7eb",
    "grid.color":       "#e5e7eb",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "DejaVu Sans",   # ships with matplotlib; supports ₹
})

def lakh(val):
    """Convert raw INR value to lakhs string."""
    return val / 1e5

# ── 1. Load & prepare ────────────────────────────────────────────────────────
df = pd.read_csv("cleaned_sales_data.csv")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df["Qty"]    = pd.to_numeric(df["Qty"],    errors="coerce").fillna(0).astype(int)
df["B2B"]    = df["B2B"].astype(str).str.strip().str.lower().map(
                   {"true": True, "false": False}).fillna(False)

fulfilled = df[~df["Status"].str.lower().str.contains("cancel", na=False)]

# ── Chart 1 — Top 10 Product Categories by Revenue (horizontal bar) ──────────
cat_rev = (fulfilled.groupby("Category")["Amount"]
           .sum().sort_values().tail(10))

fig, ax = plt.subplots(figsize=(10, 6))
colors_cat = [PALETTE_6[0] if i == len(cat_rev) - 1 else "#93c5fd"
              for i in range(len(cat_rev))]
bars = ax.barh(cat_rev.index, cat_rev.values / 1e5, color=colors_cat,
               edgecolor="none", height=0.65)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.5, bar.get_y() + bar.get_height() / 2,
            f"₹{w:,.1f}L", va="center", ha="left", fontsize=9, color=MUTED)

ax.set_xlabel("Revenue (₹ Lakhs)", labelpad=8)
ax.set_title("Top Product Categories by Net Revenue", fontsize=14, fontweight="bold", pad=14)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}L"))
ax.tick_params(axis="y", labelsize=10)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/chart1_categories.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("✔  chart1_categories.png")

# ── Chart 2 — Top 5 Shipping States by Revenue (vertical bar) ────────────────
state_rev = (fulfilled.groupby("ship-state")["Amount"]
             .sum().sort_values(ascending=False).head(5))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(state_rev.index, state_rev.values / 1e5,
              color=PALETTE_6[:5], edgecolor="none", width=0.55)

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.4,
            f"₹{h:,.1f}L", ha="center", va="bottom", fontsize=9, color=MUTED)

ax.set_ylabel("Revenue (₹ Lakhs)", labelpad=8)
ax.set_title("Top 5 Shipping States by Net Revenue", fontsize=14, fontweight="bold", pad=14)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}L"))
ax.tick_params(axis="x", labelsize=10)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/chart2_states.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("✔  chart2_states.png")

# ── Chart 3 — Fulfilment Channel Donut ───────────────────────────────────────
ful_counts = df["Fulfilment"].value_counts()
labels     = ["Amazon Easy Ship" if l == "Amazon" else "Merchant"
              for l in ful_counts.index]
colors_ful = [ACCENT, "#e2e8f0"]

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    ful_counts.values,
    labels=None,
    colors=colors_ful,
    autopct="%1.1f%%",
    pctdistance=0.78,
    startangle=90,
    wedgeprops=dict(width=0.52, edgecolor="white", linewidth=2),
)
for at in autotexts:
    at.set_fontsize(13)
    at.set_fontweight("bold")
    at.set_color("white")
autotexts[1].set_color("#374151")

ax.legend(wedges, labels, loc="lower center", ncol=2,
          frameon=False, fontsize=11, bbox_to_anchor=(0.5, -0.04))
ax.set_title("Fulfilment Channel Distribution", fontsize=14, fontweight="bold", pad=20)
# Centre label
total = ful_counts.sum()
ax.text(0, 0, f"{total:,}\nOrders", ha="center", va="center",
        fontsize=12, fontweight="bold", color="#1f2328")
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/chart3_fulfilment.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("✔  chart3_fulfilment.png")

# ── Chart 4 — Order Pipeline Status Distribution (vertical bar) ──────────────
status_counts = df["Status"].value_counts()
short_labels  = [s.replace("Shipped - ", "< ") for s in status_counts.index]

fig, ax = plt.subplots(figsize=(11, 6))
bar_colors = [ACCENT if "Shipped" in l and " - " not in l else
              "#ef4444" if "Cancel" in l else
              "#f59e0b" if "Pending" in l else "#93c5fd"
              for l in status_counts.index]

bars = ax.bar(short_labels, status_counts.values,
              color=bar_colors, edgecolor="none", width=0.6)

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 200,
            f"{h:,}", ha="center", va="bottom", fontsize=8.5, color=MUTED)

ax.set_ylabel("Order Count", labelpad=8)
ax.set_title("Order Pipeline Status Distribution", fontsize=14, fontweight="bold", pad=14)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.xticks(rotation=25, ha="right", fontsize=9)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/chart4_status.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("✔  chart4_status.png")

# ── Chart 5 — B2B vs B2C Average Order Value ─────────────────────────────────
segments = []
for label, flag in [("B2C (Consumer)", False), ("B2B (Business)", True)]:
    sub  = fulfilled[fulfilled["B2B"] == flag]
    n    = sub["Order ID"].nunique()
    avg  = sub["Amount"].sum() / n if n else 0
    segments.append({"Segment": label, "AOV": avg, "Orders": n})
seg_df = pd.DataFrame(segments)

fig, ax = plt.subplots(figsize=(7, 6))
bar_cols = ["#93c5fd", ACCENT]
bars = ax.bar(seg_df["Segment"], seg_df["AOV"], color=bar_cols,
              edgecolor="none", width=0.45)

for bar, row in zip(bars, seg_df.itertuples()):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 5,
            f"₹{h:,.2f}", ha="center", va="bottom", fontsize=11,
            fontweight="bold", color="#1f2328")
    ax.text(bar.get_x() + bar.get_width() / 2, h / 2,
            f"{row.Orders:,} orders", ha="center", va="center",
            fontsize=9, color="white", fontweight="bold")

ax.set_ylabel("Average Order Value (₹)", labelpad=8)
ax.set_title("B2B vs B2C — Average Order Value", fontsize=14, fontweight="bold", pad=14)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
ax.set_ylim(0, seg_df["AOV"].max() * 1.18)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/chart5_b2b.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("✔  chart5_b2b.png")

# ── Chart 6 — Courier Logistics Dispatch Performance ─────────────────────────
courier_counts = df["Courier Status"].value_counts()
pct_vals       = courier_counts / courier_counts.sum() * 100
colors_c       = [ACCENT if l == "Shipped" else
                  "#ef4444" if l == "Cancelled" else "#f59e0b"
                  for l in courier_counts.index]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(courier_counts.index, courier_counts.values,
               color=colors_c, edgecolor="none", height=0.5)

for bar, (label, count) in zip(bars, courier_counts.items()):
    pct = pct_vals[label]
    ax.text(bar.get_width() + 400, bar.get_y() + bar.get_height() / 2,
            f"{count:,}  ({pct:.1f}%)", va="center", fontsize=10, color=MUTED)

ax.set_xlabel("Number of Shipments", labelpad=8)
ax.set_title("Courier Logistics — Dispatch Performance", fontsize=14,
             fontweight="bold", pad=14)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlim(0, courier_counts.max() * 1.22)
ax.tick_params(axis="y", labelsize=11)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/chart6_courier.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("✔  chart6_courier.png")

print()
print(f"All 6 charts saved to '{OUTPUT_DIR}/'")
