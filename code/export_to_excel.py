import pandas as pd
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from load_data import SECTORS, OUTPUT_DIR
from portfolio_utils import (RISK_FREE_RATE, ESTIMATION_START, ESTIMATION_END, WEIGHT_LIMITS, SEED, N_SIMULATIONS,
                             HORIZON_MONTHS, INITIAL_FUND, REBALANCE_MONTHS, REBALANCE_FREQUENCIES,
                             BACKTEST_START, BACKTEST_END, PORTFOLIO_KEYS, PORTFOLIO_LABELS)

# Builds output/results.xlsx: every output table, formatted and ready to copy into the group workbook.
# It only reads the CSVs and PNGs written by the other scripts, so run it last.

# --- inputs: the csv outputs ---
allocations_df = pd.read_csv(OUTPUT_DIR / "portfolio_allocations.csv", index_col="portfolio")
summary_stats_dfs = {
    "Monthly, value-weighted":  pd.read_csv(OUTPUT_DIR / "summary_stats_monthly_vw.csv", index_col=0),
    "Monthly, equal-weighted":  pd.read_csv(OUTPUT_DIR / "summary_stats_monthly_ew.csv", index_col=0),
    "Annual, value-weighted":   pd.read_csv(OUTPUT_DIR / "summary_stats_annual_vw.csv", index_col=0),
    "Annual, equal-weighted":   pd.read_csv(OUTPUT_DIR / "summary_stats_annual_ew.csv", index_col=0),
}
correlation_df = pd.read_csv(OUTPUT_DIR / "correlation_matrix.csv", index_col=0)
covariance_df = pd.read_csv(OUTPUT_DIR / "covariance_matrix.csv", index_col=0)
forecast_summary_df = pd.read_csv(OUTPUT_DIR / "forecast_summary.csv", index_col=0)
forecast_percentiles_dfs = {portfolio: pd.read_csv(OUTPUT_DIR / f"forecast_percentiles_{portfolio}.csv", index_col="month")
                            for portfolio in PORTFOLIO_KEYS}
backtest_df = pd.read_csv(OUTPUT_DIR / "backtest_rebalancing.csv")
mc_rebalancing_df = pd.read_csv(OUTPUT_DIR / "mc_rebalancing_comparison.csv")
chart_files = ["efficient_frontier.png", "forecast_fan_A.png", "forecast_fan_B.png", "forecast_fan_C.png"]

# --- reshape into the tables shown in the workbook ---
frequency_names = {months: name for name, months in REBALANCE_FREQUENCIES.items()}   # 12 -> "Annual"
portfolio_columns = [PORTFOLIO_LABELS[portfolio] for portfolio in PORTFOLIO_KEYS]   # A, B, C order

# allocations: portfolios as columns (Low, Medium, High), returns and vols as fractions so they show as %
allocation_metrics_df = pd.DataFrame({
    PORTFOLIO_LABELS[portfolio]: {
        "Expected annual return": allocations_df.loc[key, "annualised_return"] / 100,
        "Annual volatility": allocations_df.loc[key, "annualised_vol"] / 100,
        "Sharpe ratio": allocations_df.loc[key, "sharpe"],
        "Minimum weight per sector": WEIGHT_LIMITS[key][0],
        "Maximum weight per sector": WEIGHT_LIMITS[key][1],
        "Rebalancing": frequency_names[REBALANCE_MONTHS[portfolio]],
    } for portfolio, key in PORTFOLIO_KEYS.items()})
allocation_weights_df = pd.DataFrame({PORTFOLIO_LABELS[portfolio]: allocations_df.loc[key, SECTORS]
                                      for portfolio, key in PORTFOLIO_KEYS.items()})
allocation_weights_df = allocation_weights_df.mask(allocation_weights_df.abs() < 1e-9, 0.0)   # optimiser noise like 1e-14 would show as -0.00%
allocation_weights_df.loc["Total"] = allocation_weights_df.sum()

# forecast summary: same rows, plain portfolio names as columns (the csv headers also give the rebalancing)
forecast_summary_df.columns = portfolio_columns

# five-year outcomes as "exceeded X% of the time", read from month 60 of the percentile paths
likelihood_rows = {"p5": "Exceeded 95% of the time", "p10": "Exceeded 90% of the time", "p25": "Exceeded 75% of the time",
                   "p50": "Exceeded 50% of the time (median)", "p75": "Exceeded 25% of the time",
                   "p90": "Exceeded 10% of the time", "p95": "Exceeded 5% of the time"}
forecast_likelihood_df = pd.DataFrame({PORTFOLIO_LABELS[portfolio]: percentiles_df.iloc[-1]
                                       for portfolio, percentiles_df in forecast_percentiles_dfs.items()})
forecast_likelihood_df.index = [likelihood_rows[percentile] for percentile in forecast_likelihood_df.index]

settings_df = pd.DataFrame({"Value": {
    "Estimation window": f"{ESTIMATION_START} to {ESTIMATION_END}",
    "Risk-free rate (annual)": f"{RISK_FREE_RATE:.3f}%",
    **{f"Weight limits, {PORTFOLIO_LABELS[p]}": f"{WEIGHT_LIMITS[k][0]:.0%} to {WEIGHT_LIMITS[k][1]:.0%}"
       for p, k in PORTFOLIO_KEYS.items()},
    **{f"Rebalancing, {PORTFOLIO_LABELS[p]}": frequency_names[REBALANCE_MONTHS[p]] for p in PORTFOLIO_KEYS},
    "Initial fund": f"${INITIAL_FUND:,}",
    "Simulated paths": f"{N_SIMULATIONS:,}",
    "Forecast horizon": f"{HORIZON_MONTHS} months",
    "Random seed": SEED,
    "Backtest window": f"{BACKTEST_START} to {BACKTEST_END}",
}})

# header text for each table's label column
settings_df.index.name = "Setting"
allocation_metrics_df.index.name = forecast_summary_df.index.name = "Metric"
allocation_weights_df.index.name = correlation_df.index.name = covariance_df.index.name = "Sector"
for stats_df in summary_stats_dfs.values():
    stats_df.index.name = "Sector"
forecast_likelihood_df.index.name = "Likelihood"
for percentiles_df in forecast_percentiles_dfs.values():
    percentiles_df.index.name = "Month"

# --- formatting: matches the group workbook's cleaned tables ---
PERCENT, DOLLARS, TWO_DP, THREE_DP, TIMES = "0.00%", '"$"#,##0', "0.00", "0.000", '0.00"x"'
TITLE_FONT = Font(bold=True, size=11)
HEADER_FONT, HEADER_FILL = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="002060")   # navy, white text
LABEL_FILL = PatternFill("solid", fgColor="00B0F0")                                                   # bright blue row labels
PORTFOLIO_FILLS = {PORTFOLIO_LABELS["A"]: PatternFill("solid", fgColor="C6E0B4"),   # low risk: green
                   PORTFOLIO_LABELS["B"]: PatternFill("solid", fgColor="FFE699"),   # medium risk: yellow
                   PORTFOLIO_LABELS["C"]: PatternFill("solid", fgColor="FF7C80")}   # high risk: red
THIN = Side(style="thin")
GRID = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTRED = Alignment(horizontal="center")


def write_table(sheet, df, top_row, title, column_formats=None, row_formats=None, index=True):
    """Write df with a title and a header row starting at top_row; returns the first free row below it."""
    sheet.cell(top_row, 1, title).font = TITLE_FONT
    table = df.reset_index() if index else df
    for col, header in enumerate(table.columns, start=1):
        cell = sheet.cell(top_row + 1, col, (df.index.name or "") if index and col == 1 else str(header))
        cell.font, cell.fill, cell.border, cell.alignment = HEADER_FONT, HEADER_FILL, GRID, CENTRED
    for row_offset, (row_label, row) in enumerate(zip(df.index, table.itertuples(index=False)), start=2):
        for col, value in enumerate(row, start=1):
            cell = sheet.cell(top_row + row_offset, col, value)
            cell.border = GRID
            header = table.columns[col - 1]
            number_format = (row_formats or {}).get(row_label) or (column_formats or {}).get(header)
            if value in PORTFOLIO_FILLS:          # portfolio names coloured by risk level
                cell.fill = PORTFOLIO_FILLS[value]
            elif index and col == 1:              # row labels
                cell.fill = LABEL_FILL
            elif number_format and isinstance(value, (int, float)):
                cell.number_format = number_format
    return top_row + len(table) + 3


def fit_columns(sheet, min_width=10, max_width=45):
    """Size each column to its longest entry, ignoring table titles (they can overflow into the next cells)."""
    for column in sheet.columns:
        lengths = [len(str(cell.value)) for cell in column if cell.value is not None and cell.font != TITLE_FONT]
        width = max(lengths, default=0) + 2
        sheet.column_dimensions[get_column_letter(column[0].column)].width = min(max(width, min_width), max_width)


workbook = Workbook()

sheet = workbook.active
sheet.title = "Settings"
write_table(sheet, settings_df, 1, "Settings used for these results")

sheet = workbook.create_sheet("Allocations")
next_row = write_table(sheet, allocation_metrics_df, 1, "Portfolio summary",
                       row_formats={"Expected annual return": PERCENT, "Annual volatility": PERCENT, "Sharpe ratio": THREE_DP,
                                    "Minimum weight per sector": "0%", "Maximum weight per sector": "0%"})
write_table(sheet, allocation_weights_df, next_row, "Sector weights", column_formats=dict.fromkeys(portfolio_columns, PERCENT))

sheet = workbook.create_sheet("Summary stats")
next_row = 1
for title, stats_df in summary_stats_dfs.items():
    stats_formats = {column: (THREE_DP if "Sharpe" in column else "0" if column == "Observations" else TWO_DP)
                     for column in stats_df.columns}
    next_row = write_table(sheet, stats_df, next_row, f"{title} returns, {ESTIMATION_START[:4]}-{ESTIMATION_END[:4]} (% units)",
                           column_formats=stats_formats)

sheet = workbook.create_sheet("Correlation")
write_table(sheet, correlation_df, 1, "Correlation of monthly returns", column_formats=dict.fromkeys(SECTORS, TWO_DP))
sheet.conditional_formatting.add(f"B3:{get_column_letter(len(SECTORS) + 1)}{len(SECTORS) + 2}",
                                 ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                end_type="num", end_value=1, end_color="F8696B"))

sheet = workbook.create_sheet("Covariance")
write_table(sheet, covariance_df, 1, "Covariance of monthly returns (%²)", column_formats=dict.fromkeys(SECTORS, TWO_DP))

sheet = workbook.create_sheet("Forecast")
next_row = write_table(sheet, forecast_summary_df, 1, f"Five-year forecast, {N_SIMULATIONS:,} simulated paths from ${INITIAL_FUND:,}",
                       row_formats={"Mean": DOLLARS, "Median": DOLLARS, "5th pct": DOLLARS, "10th pct": DOLLARS,
                                    "90th pct": DOLLARS, "95th pct": DOLLARS, "P(loss)": PERCENT, "SE of P(loss)": PERCENT,
                                    "Median growth p.a.": PERCENT})
write_table(sheet, forecast_likelihood_df, next_row, "Fund value after five years", column_formats=dict.fromkeys(portfolio_columns, DOLLARS))

for portfolio, percentiles_df in forecast_percentiles_dfs.items():
    sheet = workbook.create_sheet(f"Fan chart data {portfolio}")
    write_table(sheet, percentiles_df, 1, f"{PORTFOLIO_LABELS[portfolio]}: fund value percentiles by month",
                column_formats=dict.fromkeys(percentiles_df.columns, DOLLARS))
    sheet.freeze_panes = "B3"

sheet = workbook.create_sheet("Backtest")
write_table(sheet, backtest_df, 1, f"Historical backtest, {BACKTEST_START} to {BACKTEST_END}, from ${INITIAL_FUND:,}",
            column_formats={"Final value ($)": DOLLARS, "Total return": PERCENT, "Annualised vol": PERCENT,
                            "Max drawdown": PERCENT, "Turnover": TIMES}, index=False)

sheet = workbook.create_sheet("Rebalancing MC")
write_table(sheet, mc_rebalancing_df, 1, f"Rebalancing frequencies compared on the same {N_SIMULATIONS:,} simulated paths",
            column_formats={"Mean": DOLLARS, "Median": DOLLARS, "5th pct": DOLLARS, "P(loss)": PERCENT}, index=False)

for sheet in workbook.worksheets:
    fit_columns(sheet)

sheet = workbook.create_sheet("Charts")
image_row = 1
for chart_file in chart_files:
    chart = Image(OUTPUT_DIR / chart_file)
    scale = 800 / chart.width   # same on-screen width for every chart
    chart.width, chart.height = chart.width * scale, chart.height * scale
    sheet.add_image(chart, f"A{image_row}")
    image_row += int(chart.height / 20) + 2   # default row height is 20 px

workbook_path = OUTPUT_DIR / "results.xlsx"
try:
    workbook.save(workbook_path)
except PermissionError:
    raise SystemExit(f"Could not write {workbook_path}: close it in Excel and run again.")
print(f"Workbook saved to output/results.xlsx ({len(workbook.sheetnames)} tabs: {', '.join(workbook.sheetnames)})")
