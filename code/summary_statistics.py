import numpy as np
from load_data import sections, SECTORS, OUTPUT_DIR

# ---------------------------------------------------------------------------
# Source data
# ---------------------------------------------------------------------------
monthly_vw_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].copy()
monthly_ew_returns = sections["Average Equal Weighted Returns -- Monthly"][SECTORS].copy()
annual_vw_returns  = sections["Average Value Weighted Returns -- Annual"][SECTORS].copy()
annual_ew_returns  = sections["Average Equal Weighted Returns -- Annual"][SECTORS].copy()

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def summary_stats(df, freq):
    """
    Compute summary statistics for a DataFrame of returns.

    freq: "monthly" or "annual" — used to annualise mean and vol correctly.
    """
    periods = 12 if freq == "monthly" else 1

    stats = df.agg(["mean", "std", "min", "max"]).T
    stats.columns = ["Mean return (%)", "Std dev (%)", "Min (%)", "Max (%)"]
    stats["Annualised mean (%)"] = stats["Mean return (%)"] * periods
    stats["Annualised vol (%)"]  = stats["Std dev (%)"] * np.sqrt(periods)
    stats["Sharpe (ann., rf=0)"] = stats["Annualised mean (%)"] / stats["Annualised vol (%)"]
    stats["Observations"]        = df.count().astype(int)

    return stats.round(4)

# ---------------------------------------------------------------------------
# Compute and write
# ---------------------------------------------------------------------------
outputs = {
    "summary_stats_monthly_vw.csv": summary_stats(monthly_vw_returns, "monthly"),
    "summary_stats_monthly_ew.csv": summary_stats(monthly_ew_returns, "monthly"),
    "summary_stats_annual_vw.csv":  summary_stats(annual_vw_returns,  "annual"),
    "summary_stats_annual_ew.csv":  summary_stats(annual_ew_returns,  "annual"),
}

for filename, stats in outputs.items():
    path = OUTPUT_DIR / filename
    stats.to_csv(path)
    print(f"Written {filename}:")
    print(stats.to_string())
    print()
