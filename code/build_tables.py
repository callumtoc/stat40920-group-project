from load_data import sections, SECTORS, CLEANED_DIR

SECTION_TO_FILE = {
    "Average Value Weighted Returns -- Monthly":  "monthly_vw_returns.csv",
    "Average Equal Weighted Returns -- Monthly":  "monthly_ew_returns.csv",
    "Average Value Weighted Returns -- Annual":   "annual_vw_returns.csv",
    "Average Equal Weighted Returns -- Annual":   "annual_ew_returns.csv",
    "Number of Firms in Portfolios":              "number_of_firms.csv",
    "Average Firm Size":                          "average_firm_size.csv",
    "Sum of BE / Sum of ME":                      "sum_be_me.csv",
    "Value-Weighted Average of BE/ME":            "average_be_me.csv",
}

for section_name, filename in SECTION_TO_FILE.items():
    section_df = sections[section_name]
    available = [s for s in SECTORS if s in section_df.columns]
    out = section_df[available].copy()
    out.to_csv(CLEANED_DIR / filename)
    print(f"Written {filename}: {out.shape}")
