"""
load_data.py

Loads the monthly value-weighted returns for our ten sectors from the
Kenneth French 49 Industry Portfolios CSV.

Exposes:
    df      -- DataFrame of monthly returns (%), indexed by date
    SECTORS -- list of sector column names
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "49_Industry_Portfolios.csv"

SECTORS = ["Clths", "Hlth", "MedEq", "Drugs", "Mach", "ElcEq", "Autos", "Paper", "Boxes", "Trans"]

df_all = pd.read_csv(
    RAW_FILE,
    skiprows=11,        # skip preamble; row 12 (0-indexed 11) is the header
    nrows=1203,         # monthly VW section only
    index_col=0,
    na_values=[-99.99, -999],
)

df_all.index = pd.to_datetime(df_all.index.astype(str), format="%Y%m")
df_all.index.name = "date"
df_all.columns = df_all.columns.str.strip()

df = df_all[SECTORS].copy()

if __name__ == "__main__":
    print(f"Data loaded: {len(df)} monthly observations ({df.index[0].strftime('%b %Y')} – {df.index[-1].strftime('%b %Y')})")
    print(df.head())
