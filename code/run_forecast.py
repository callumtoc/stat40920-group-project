import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_data import SECTORS, OUTPUT_DIR
from portfolio_utils import (monthly_vw_returns, monthly_mean_returns, monthly_cov_matrix,
                             SEED, N_SIMULATIONS, HORIZON_MONTHS, INITIAL_FUND, REBALANCE_MONTHS,
                             REBALANCE_FREQUENCIES, BACKTEST_START, BACKTEST_END, PORTFOLIO_KEYS, PORTFOLIO_LABELS)
from simulation import simulate_fund, backtest_metrics, simulate_returns, summarise, fan_chart

# the repo stores returns in %, the simulation works in decimals
monthly_mean_returns_decimal = monthly_mean_returns / 100
monthly_cov_matrix_decimal = monthly_cov_matrix / 100**2
backtest_returns = (monthly_vw_returns.loc[BACKTEST_START:BACKTEST_END] / 100).to_numpy()
allocations_df = pd.read_csv(OUTPUT_DIR / "portfolio_allocations.csv", index_col=0)
portfolio_weights = {portfolio: allocations_df.loc[name, SECTORS].to_numpy(float)
                     for portfolio, name in PORTFOLIO_KEYS.items()}

# historical backtest of every rebalancing frequency
backtest_rows = []
for portfolio, weights in portfolio_weights.items():
    for frequency, rebalance_every in REBALANCE_FREQUENCIES.items():
        fund_values = simulate_fund(weights, backtest_returns, rebalance_every, INITIAL_FUND)
        backtest_rows.append({"Portfolio": PORTFOLIO_LABELS[portfolio], "Rebalancing": frequency,
                              **backtest_metrics(fund_values, weights, backtest_returns, rebalance_every)})
backtest_df = pd.DataFrame(backtest_rows).set_index(["Portfolio", "Rebalancing"])

# Monte Carlo forecast: all portfolios share the same simulated returns
simulated_returns = simulate_returns(monthly_mean_returns_decimal, monthly_cov_matrix_decimal,
                                     N_SIMULATIONS, HORIZON_MONTHS, SEED)
simulated_fund_values = {portfolio: simulate_fund(weights, simulated_returns, REBALANCE_MONTHS[portfolio], INITIAL_FUND)
                         for portfolio, weights in portfolio_weights.items()}
forecast_summary_df = pd.DataFrame({f"{PORTFOLIO_LABELS[portfolio]}, rebalance every {REBALANCE_MONTHS[portfolio]}m":
                                    summarise(fund_values[:, -1], INITIAL_FUND)
                                    for portfolio, fund_values in simulated_fund_values.items()})

# every rebalancing frequency inside the simulation
mc_rebalancing_rows = []
for portfolio, weights in portfolio_weights.items():
    for frequency, rebalance_every in REBALANCE_FREQUENCIES.items():
        stats = summarise(simulate_fund(weights, simulated_returns, rebalance_every, INITIAL_FUND)[:, -1], INITIAL_FUND)
        mc_rebalancing_rows.append({"Portfolio": PORTFOLIO_LABELS[portfolio], "Rebalancing": frequency,
                                    "Mean": stats["Mean"], "Median": stats["Median"],
                                    "5th pct": stats["5th pct"], "P(loss)": stats["P(loss)"]})
mc_rebalancing_df = pd.DataFrame(mc_rebalancing_rows).set_index(["Portfolio", "Rebalancing"])

backtest_df.to_csv(OUTPUT_DIR / "backtest_rebalancing.csv")
forecast_summary_df.to_csv(OUTPUT_DIR / "forecast_summary.csv")
mc_rebalancing_df.to_csv(OUTPUT_DIR / "mc_rebalancing_comparison.csv")
for portfolio, fund_values in simulated_fund_values.items():
    percentiles_df = pd.DataFrame({f"p{q}": np.percentile(fund_values, q, axis=0) for q in (5, 10, 25, 50, 75, 90, 95)})
    percentiles_df.index.name = "month"
    percentiles_df.to_csv(OUTPUT_DIR / f"forecast_percentiles_{portfolio}.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fan_chart(fund_values, f"{PORTFOLIO_LABELS[portfolio]}: simulated five-year value", ax, INITIAL_FUND)
    ax.legend(loc="upper left"); fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"forecast_fan_{portfolio}.png", dpi=200); plt.close(fig)

print(backtest_df[["Final value ($)", "Total return", "Max drawdown", "Turnover"]].to_string())
print(forecast_summary_df.to_string())
