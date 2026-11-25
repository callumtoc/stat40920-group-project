import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_data import SECTORS, OUTPUT_DIR, ff_factors
from portfolio_utils import (monthly_vw_returns, INITIAL_FUND, REBALANCE_MONTHS, PORTFOLIO_KEYS, PORTFOLIO_LABELS,
                             HISTORY_START, HISTORY_END, CRISIS_PERIODS)
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