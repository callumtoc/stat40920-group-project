import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "49_Industry_Portfolios.csv"
FF_FACTORS_FILE = ROOT / "data" / "raw" / "F-F_Research_Data_Factors.csv"
CLEANED_DIR = ROOT / "data" / "cleaned"
CLEANED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SECTORS = ["Clths", "Hlth", "MedEq", "Drugs", "Mach", "ElcEq", "Autos", "Paper", "Boxes", "Trans"]

# ---------------------------------------------------------------------------
# Parse the whole file into sections
# ---------------------------------------------------------------------------
raw_lines = pd.Series(open(RAW_FILE).readlines())

# Section header lines are indented with two spaces followed by a letter (not a digit or comma)
header_mask = raw_lines.str.match(r"^  [A-Za-z]")
header_indices = raw_lines[header_mask].index.tolist()

sections = {}
for i, start in enumerate(header_indices):
    name = raw_lines[start].strip()
    col_line = start + 1          # column names are always the next line
    data_start = start + 2        # data rows begin after that

    # Data ends at the next blank line (or end of file)
    end = header_indices[i + 1] - 1 if i + 1 < len(header_indices) else len(raw_lines)
    data_lines = raw_lines[data_start:end]
    data_lines = data_lines[data_lines.str.strip() != ""]

    cols = [c.strip() for c in raw_lines[col_line].strip().lstrip(",").split(",")]

    rows = []
    for line in data_lines:
        parts = line.strip().split(",")
        values = [None if float(v.strip()) in (-99.99, -999.0) else float(v.strip()) for v in parts[1:]]
        rows.append([parts[0].strip()] + values)

    section_df = pd.DataFrame(rows, columns=["date"] + cols)
    # Annual sections use YYYY format; monthly sections use YYYYMM
    annual = "Annual" in name or "BE/ME" in name or "Sum of BE" in name
    fmt = "%Y" if annual else "%Y%m"
    section_df["date"] = pd.to_datetime(section_df["date"], format=fmt, errors="coerce")
    section_df = section_df.dropna(subset=["date"]).set_index("date")

    sections[name] = section_df

# ---------------------------------------------------------------------------
# Fama/French 3 Factors file: risk-free rate (RF) and market return (Mkt)
# ---------------------------------------------------------------------------
ff_rows = []
for line in open(FF_FACTORS_FILE):
    parts = [p.strip() for p in line.split(",")]
    # keep monthly rows only: first field is a 6-digit date YYYYMM
    # (skips text lines, the column header and the annual YYYY rows at the bottom)
    if len(parts) >= 5 and len(parts[0]) == 6 and parts[0].isdigit():
        ff_rows.append(parts[:5])

ff_factors = pd.DataFrame(ff_rows, columns=["date", "Mkt-RF", "SMB", "HML", "RF"])
ff_factors["date"] = pd.to_datetime(ff_factors["date"], format="%Y%m")
ff_factors = ff_factors.set_index("date").astype(float)  # monthly %, same units as sector returns
ff_factors["Mkt"] = ff_factors["Mkt-RF"] + ff_factors["RF"]  # total market return (benchmark/beta later)

# assert if parsing goes wrong (~1,200 monthly rows expected)
assert len(ff_factors) > 1000, "Fama/French factors file parsed incorrectly"
