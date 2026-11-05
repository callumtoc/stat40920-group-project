"""
summary_stats.py

Imports the cleaned returns DataFrame from load_data.py and writes:
    output/returns.csv       -- cleaned monthly returns for our ten sectors
    output/summary_stats.csv -- summary statistics table
"""

import numpy as np
from pathlib import Path
from load_data import df, SECTORS

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Save cleaned returns
# ---------------------------------------------------------------------------
returns_path = OUTPUT_DIR / "returns.csv"
df.to_csv(returns_path)
print(f"Returns written to {returns_path}")

# ---------------------------------------------------------------------------
# Summary statistics (returns are in %)
# ---------------------------------------------------------------------------
stats = df.agg(["mean", "std", "min", "max"]).T
stats.columns = ["Mean (%/month)", "Std dev (%/month)", "Min (%)", "Max (%)"]
stats["Annualised mean (%)"] = df.mean() * 12
stats["Annualised vol (%)"]  = df.std() * np.sqrt(12)
stats["Sharpe (ann., rf=0)"] = stats["Annualised mean (%)"] / stats["Annualised vol (%)"]
stats["Observations"]        = df.count().astype(int)
stats = stats.round(4)

stats_path = OUTPUT_DIR / "summary_stats.csv"
stats.to_csv(stats_path)
print(f"Summary statistics written to {stats_path}")
print()
print(stats.to_string())
