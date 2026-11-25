import pandas as pd
import matplotlib.pyplot as plt
from load_data import OUTPUT_DIR
from portfolio_utils import monthly_vw_returns, WEIGHT_LIMITS, ESTIMATION_START, ESTIMATION_END

frontier_df = pd.read_csv(OUTPUT_DIR / "efficient_frontier.csv")
allocations_df = pd.read_csv(OUTPUT_DIR / "portfolio_allocations.csv", index_col="portfolio")

# individual sector risk/return for reference points
sector_returns = monthly_vw_returns.mean() * 12
sector_vols = monthly_vw_returns.std() * (12 ** 0.5)

fig, ax = plt.subplots(figsize=(10, 6))

colors = {"low_risk": "green", "medium_risk": "orange", "high_risk": "red"}
labels = {"low_risk": "Low risk", "medium_risk": "Medium risk", "high_risk": "High risk"}

# one frontier per constraint set, in the same colour as the portfolio built under it
for portfolio, (lower, upper) in WEIGHT_LIMITS.items():
    curve = frontier_df[frontier_df["constraint_set"] == portfolio]
    ax.plot(curve["annualised_vol"], curve["annualised_return"], color=colors[portfolio], lw=1.5, alpha=0.7,
            label=f"Frontier, weights {lower:.0%} to {upper:.0%}")
for name, row in allocations_df.iterrows():
    ax.scatter(row["annualised_vol"], row["annualised_return"], color=colors[name], s=100, zorder=5, label=labels[name])

# cap the x-axis so Paper (~52% vol, driven by 1930s months) doesn't squash the frontier; it's drawn as an arrow at the edge
VOL_AXIS_MAX = 32
on_chart = sector_vols <= VOL_AXIS_MAX
ax.scatter(sector_vols[on_chart], sector_returns[on_chart], color="grey", s=40, alpha=0.6, zorder=4, label="Individual sectors")
for sector in sector_vols[on_chart].index:
    ax.annotate(sector, (sector_vols[sector], sector_returns[sector]), textcoords="offset points", xytext=(5, 3), fontsize=7, color="grey")
for sector in sector_vols[~on_chart].index:
    ax.scatter(VOL_AXIS_MAX - 0.3, sector_returns[sector], marker=">", color="grey", s=60, alpha=0.6, zorder=4)
    ax.annotate(f"{sector} ({sector_vols[sector]:.0f}% vol)", (VOL_AXIS_MAX - 0.3, sector_returns[sector]),
                textcoords="offset points", xytext=(-8, -3), ha="right", fontsize=7, color="grey")
ax.set_xlim(right=VOL_AXIS_MAX)


ax.set_xlabel("Annualised volatility (%)")
ax.set_ylabel("Annualised return (%)")
ax.set_title(f"Efficient frontiers under each portfolio's weight limits ({ESTIMATION_START[:4]}–{ESTIMATION_END[:4]})")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "efficient_frontier.png", dpi=150)
print("Chart saved to output/efficient_frontier.png")
plt.show()
