import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "49_Industry_Portfolios.csv"
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
    section_df["date"] = pd.to_datetime(section_df["date"], format="%Y%m", errors="coerce")
    section_df = section_df.dropna(subset=["date"]).set_index("date")

    sections[name] = section_df

# ---------------------------------------------------------------------------
# Shorthand for the section we'll use most
# ---------------------------------------------------------------------------
monthly_vw_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].copy()

# Write cleaned returns to output
monthly_vw_returns.to_csv(OUTPUT_DIR / "monthly_vw_returns.csv")

if __name__ == "__main__":
    print("Sections parsed:")
    for name, section_df in sections.items():
        print(f"  '{name}': {section_df.shape}")
    print(f"\nmonthly_vw_returns (our 10 sectors): {monthly_vw_returns.shape}")
    print(f"Returns written to {OUTPUT_DIR / 'monthly_vw_returns.csv'}")
