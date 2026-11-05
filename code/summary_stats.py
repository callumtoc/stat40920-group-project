"""
summary_stats.py

Imports the cleaned returns DataFrame from load_data.py and writes:
    output/monthly_vw_returns.csv -- cleaned monthly returns for our ten sectors
    output/summary_stats.csv -- summary statistics table
"""

import numpy as np
from pathlib import Path
from load_data import monthly_vw_returns, SECTORS

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# ---------------------------------------------------------------------------
# Summary statistics (returns are in %)
# ---------------------------------------------------------------------------
stats = monthly_vw_returns.agg(["mean", "std", "min", "max"]).T
stats.columns = ["Mean (%/month)", "Std dev (%/month)", "Min (%)", "Max (%)"]
stats["Annualised mean (%)"] = monthly_vw_returns.mean() * 12
stats["Annualised vol (%)"]  = monthly_vw_returns.std() * np.sqrt(12)
stats["Sharpe (ann., rf=0)"] = stats["Annualised mean (%)"] / stats["Annualised vol (%)"]
stats["Observations"]        = monthly_vw_returns.count().astype(int)
stats = stats.round(4)

stats_path = OUTPUT_DIR / "summary_stats.csv"
stats.to_csv(stats_path)
print(f"Summary statistics written to {stats_path}")
print()
print(stats.to_string())
