import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from load_data import SECTORS, OUTPUT_DIR, ff_factors, sections
from portfolio_utils import (monthly_vw_returns, INITIAL_FUND, REBALANCE_MONTHS, PORTFOLIO_KEYS, PORTFOLIO_LABELS,
                             HISTORY_START, HISTORY_END, CRISIS_PERIODS, ESTIMATION_START, OUT_OF_SAMPLE_END,
                             WEIGHT_LIMITS, CONS_SUM, W0, bounds_for)
from simulation import simulate_fund, backtest_metrics

# how each recommended portfolio (at its chosen rebalancing frequency) would have performed vs the whole market
# note: weights were estimated on 1970-2025 data, which includes this period, so this flatters the portfolios
history_returns = monthly_vw_returns.loc[HISTORY_START:HISTORY_END] / 100           # decimals
market_returns = ff_factors["Mkt"].reindex(history_returns.index) / 100              # total US market return
assert market_returns.notna().all(), "market return missing for some months"
allocations_df = pd.read_csv(OUTPUT_DIR / "portfolio_allocations.csv", index_col=0)

# fund values: month 0 is the starting $1m, month m is the value at the end of month m
fund_values = {}
for portfolio, name in PORTFOLIO_KEYS.items():
    weights = allocations_df.loc[name, SECTORS].to_numpy(float)
    fund_values[PORTFOLIO_LABELS[portfolio]] = simulate_fund(weights, history_returns.to_numpy(),
                                                             REBALANCE_MONTHS[portfolio], INITIAL_FUND)
fund_values["US market"] = INITIAL_FUND * np.concatenate([[1], np.cumprod(1 + market_returns.to_numpy())])
start_label = history_returns.index[0] - pd.DateOffset(months=1)                     # value before the first month
fund_values_df = pd.DataFrame(fund_values, index=[start_label, *history_returns.index])

# summary table: final value, annualised return, volatility, max drawdown
n_years = len(history_returns) / 12
rows = []
for name, values in fund_values_df.items():
    metrics = backtest_metrics(values.to_numpy(), np.array([1.0]), np.zeros((len(values) - 1, 1)), None)
    rows.append({"Portfolio": name, "Final value ($)": metrics["Final value ($)"],
                 "Annualised return": (metrics["Final value ($)"] / INITIAL_FUND) ** (1 / n_years) - 1,
                 "Annualised vol": metrics["Annualised vol"], "Max drawdown": metrics["Max drawdown"]})
performance_df = pd.DataFrame(rows).set_index("Portfolio")

# return over each crisis: value at the end of the last month / value just before the first month
crisis_df = pd.DataFrame({
    f"{crisis} ({start} to {end})": fund_values_df.iloc[fund_values_df.index.get_loc(pd.Timestamp(end))]
                                    / fund_values_df.iloc[fund_values_df.index.get_loc(pd.Timestamp(start)) - 1] - 1
    for crisis, (start, end) in CRISIS_PERIODS.items()})

# chart: growth of $1m, direct labels at the line ends (colours alone don't identify the lines)
colors = {PORTFOLIO_LABELS["A"]: "#257de0", PORTFOLIO_LABELS["B"]: "#f47230", PORTFOLIO_LABELS["C"]: "#00b894",
          "US market": "#6b6b6b"}
fig, ax = plt.subplots(figsize=(9, 5))
for name, values in fund_values_df.items():
    ax.plot(values.index, values / 1e6, color=colors[name], lw=2, ls="--" if name == "US market" else "-", label=name)
    ax.annotate(f"{name.split(' (')[0]}  \\${values.iloc[-1] / 1e6:.1f}m", (values.index[-1], values.iloc[-1] / 1e6),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color="#333333")
for start, end in CRISIS_PERIODS.values():
    ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color="#dddddd", alpha=0.5, lw=0)
ax.axhline(INITIAL_FUND / 1e6, color="#999999", lw=0.8)
ax.set_ylabel("Value of \\$1m invested (\\$m)")   # \\$ = a literal $ in matplotlib
ax.set_title(f"Growth of \\$1m, {HISTORY_START[:4]}–{HISTORY_END[:4]} (shaded: crisis periods)")
ax.legend(loc="upper left", frameon=False)
ax.grid(True, alpha=0.3)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.set_xlim(right=values.index[-1] + pd.DateOffset(years=2))   # room for the end labels
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "historical_growth.png", dpi=200)
plt.close(fig)

fund_values_df.to_csv(OUTPUT_DIR / "historical_fund_values.csv")
performance_df.to_csv(OUTPUT_DIR / "historical_performance.csv")
crisis_df.to_csv(OUTPUT_DIR / "historical_crises.csv")
print(performance_df.to_string(formatters={"Final value ($)": "${:,.0f}".format, "Annualised return": "{:.2%}".format,
                                           "Annualised vol": "{:.2%}".format, "Max drawdown": "{:.2%}".format}))
print()
print(crisis_df.to_string(float_format="{:.1%}".format))


# --- out-of-sample check ---------------------------------------------------------------------------------------
# same rules as calculate_portfolio_allocations.py (A min variance, C max Sharpe, B min variance at the midpoint
# return, each under its WEIGHT_LIMITS), but estimated only on ESTIMATION_START to OUT_OF_SAMPLE_END
oos_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].loc[ESTIMATION_START:OUT_OF_SAMPLE_END]
oos_mean, oos_cov = oos_returns.mean().values, oos_returns.cov().values
oos_rf = ff_factors["RF"].reindex(oos_returns.index).mean() * 12            # e over the same months, annual %

def oos_stats(w):
    return w @ oos_mean * 12, np.sqrt(w @ oos_cov @ w * 12)                 # annualised (return %, vol %)

def solve(objective, portfolio, extra_constraints=()):
    result = minimize(objective, W0, method="SLSQP", bounds=bounds_for(portfolio),
                      constraints=[CONS_SUM, *extra_constraints])
    assert result.success, f"out-of-sample {portfolio}: optimiser failed - {result.message}"
    return result.x

oos_weights = {"low_risk": solve(lambda w: oos_stats(w)[1], "low_risk"),
               "high_risk": solve(lambda w: -(oos_stats(w)[0] - oos_rf) / oos_stats(w)[1], "high_risk")}
mid_target = (oos_stats(oos_weights["low_risk"])[0] + oos_stats(oos_weights["high_risk"])[0]) / 2
oos_weights["medium_risk"] = solve(lambda w: oos_stats(w)[1], "medium_risk",
                                   [{"type": "eq", "fun": lambda w: oos_stats(w)[0] - mid_target}])

oos_rows, oos_values = [], {}
for portfolio, name in PORTFOLIO_KEYS.items():
    values = simulate_fund(oos_weights[name], history_returns.to_numpy(), REBALANCE_MONTHS[portfolio], INITIAL_FUND)
    oos_values[PORTFOLIO_LABELS[portfolio]] = values
    drawdowns = values / np.maximum.accumulate(values) - 1
    oos_rows.append({"Portfolio": PORTFOLIO_LABELS[portfolio], "Final value ($)": values[-1],
                     "Annualised return": (values[-1] / INITIAL_FUND) ** (1 / n_years) - 1,
                     "Max drawdown": drawdowns.min(),
                     "In-sample final value ($)": fund_values_df[PORTFOLIO_LABELS[portfolio]].iloc[-1],
                     **{sector: weight for sector, weight in zip(SECTORS, oos_weights[name])}})
oos_rows.append({"Portfolio": "US market", "Final value ($)": fund_values_df["US market"].iloc[-1],
                 "Annualised return": performance_df.loc["US market", "Annualised return"],
                 "Max drawdown": performance_df.loc["US market", "Max drawdown"],
                 "In-sample final value ($)": fund_values_df["US market"].iloc[-1]})
oos_df = pd.DataFrame(oos_rows).set_index("Portfolio")
oos_df.to_csv(OUTPUT_DIR / "historical_out_of_sample.csv")

print(f"\nOut-of-sample check: portfolios estimated on {ESTIMATION_START} to {OUT_OF_SAMPLE_END} "
      f"(e = {oos_rf:.2f}%), measured over {HISTORY_START} to {HISTORY_END}")
print(oos_df[["Final value ($)", "Annualised return", "Max drawdown", "In-sample final value ($)"]].to_string(
    formatters={"Final value ($)": "${:,.0f}".format, "Annualised return": "{:.2%}".format,
                "Max drawdown": "{:.2%}".format, "In-sample final value ($)": "${:,.0f}".format}))

# chart: in-sample vs out-of-sample growth of $1m, side by side on the same scale
oos_values["US market"] = fund_values_df["US market"].to_numpy()
oos_values_df = pd.DataFrame(oos_values, index=fund_values_df.index)
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
panels = [(f"In-sample: estimated {ESTIMATION_START[:4]}–2025", fund_values_df),
          (f"Out-of-sample: estimated {ESTIMATION_START[:4]}–{OUT_OF_SAMPLE_END[:4]} only", oos_values_df)]
for ax, (title, values_df) in zip(axes, panels):
    # end labels, nudged apart so lines finishing at similar values don't overlap
    label_y = values_df.iloc[-1].sort_values() / 1e6
    for i in range(1, len(label_y)):
        label_y.iloc[i] = max(label_y.iloc[i], label_y.iloc[i - 1] + 0.5)
    for name, values in values_df.items():
        ax.plot(values.index, values / 1e6, color=colors[name], lw=2, ls="--" if name == "US market" else "-",
                label=name)
        ax.annotate(f"{name.split(' (')[0]}  \\${values.iloc[-1] / 1e6:.1f}m", (values.index[-1], label_y[name]),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color="#333333")
    ax.axhline(INITIAL_FUND / 1e6, color="#999999", lw=0.8)
    ax.set_title(title, fontsize=11)
    ax.set_xlim(right=values.index[-1] + pd.DateOffset(years=3))   # room for the end labels
    ax.grid(True, alpha=0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].set_ylabel("Value of \\$1m invested (\\$m)")
axes[0].legend(loc="upper left", frameon=False, fontsize=9)
fig.suptitle(f"Growth of \\$1m, {HISTORY_START[:4]}–{HISTORY_END[:4]}: portfolios built with and without hindsight")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "historical_out_of_sample.png", dpi=200)
plt.close(fig)