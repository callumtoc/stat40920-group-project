import pandas as pd
import matplotlib.pyplot as plt
from load_data import SECTORS, OUTPUT_DIR
from portfolio_utils import monthly_vw_returns, ALLOW_SHORT

frontier_df = pd.read_csv(OUTPUT_DIR / "efficient_frontier.csv")
allocations_df = pd.read_csv(OUTPUT_DIR / "portfolio_allocations.csv", index_col="portfolio")

# individual sector risk/return for reference points
sector_returns = monthly_vw_returns.mean() * 12
sector_vols = monthly_vw_returns.std() * (12 ** 0.5)

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(frontier_df["annualised_vol"], frontier_df["annualised_return"], color="steelblue", lw=2, label="Efficient frontier")

colors = {"low_risk": "green", "medium_risk": "orange", "high_risk": "red"}
labels = {"low_risk": "Low risk", "medium_risk": "Medium risk", "high_risk": "High risk"}
for name, row in allocations_df.iterrows():
    ax.scatter(row["annualised_vol"], row["annualised_return"], color=colors[name], s=100, zorder=5, label=labels[name])

ax.scatter(sector_vols, sector_returns, color="grey", s=40, alpha=0.6, zorder=4, label="Individual sectors")
for sector in SECTORS:
    ax.annotate(sector, (sector_vols[sector], sector_returns[sector]), textcoords="offset points", xytext=(5, 3), fontsize=7, color="grey")

short_note = "(short selling allowed)" if ALLOW_SHORT else "(long-only)"
ax.set_xlabel("Annualised volatility (%)")
ax.set_ylabel("Annualised return (%)")
ax.set_title(f"Efficient Frontier — 10 Sector Portfolios {short_note}")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "efficient_frontier.png", dpi=150)
print("Chart saved to output/efficient_frontier.png")
plt.show()
