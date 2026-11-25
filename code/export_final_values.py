import pandas as pd
from load_data import SECTORS, OUTPUT_DIR
from portfolio_utils import (monthly_mean_returns, monthly_cov_matrix, SEED, N_SIMULATIONS, HORIZON_MONTHS,
                             INITIAL_FUND, REBALANCE_FREQUENCIES, PORTFOLIO_KEYS, PORTFOLIO_LABELS)
from simulation import simulate_fund, simulate_returns

# same inputs and seed as run_forecast.py, so these are the exact paths behind forecast_summary.csv
# and mc_rebalancing_comparison.csv
monthly_mean_returns_decimal = monthly_mean_returns / 100   # the repo stores returns in %, the simulation works in decimals
monthly_cov_matrix_decimal = monthly_cov_matrix / 100**2
allocations_df = pd.read_csv(OUTPUT_DIR / "portfolio_allocations.csv", index_col=0)
portfolio_weights = {portfolio: allocations_df.loc[name, SECTORS].to_numpy(float)
                     for portfolio, name in PORTFOLIO_KEYS.items()}

# one column per portfolio and rebalancing frequency (3 x 4 = 12); every column uses the same simulated
# returns, so row k is the same simulated future in all 12 columns
simulated_returns = simulate_returns(monthly_mean_returns_decimal, monthly_cov_matrix_decimal,
                                     N_SIMULATIONS, HORIZON_MONTHS, SEED)
final_values_df = pd.DataFrame({f"{PORTFOLIO_LABELS[portfolio]}, {frequency}":
                                simulate_fund(weights, simulated_returns, rebalance_every, INITIAL_FUND)[:, -1]
                                for portfolio, weights in portfolio_weights.items()
                                for frequency, rebalance_every in REBALANCE_FREQUENCIES.items()})
final_values_df.index.name = "path"

final_values_df.to_csv(OUTPUT_DIR / "forecast_final_values.csv")
print(f"Saved {len(final_values_df):,} simulated final values for {final_values_df.shape[1]} portfolio/rebalancing "
      "combinations to output/forecast_final_values.csv")
print(final_values_df.describe().T.to_string(float_format="{:,.0f}".format))
