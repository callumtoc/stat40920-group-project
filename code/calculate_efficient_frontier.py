import numpy as np
import pandas as pd
from scipy.optimize import minimize
from load_data import OUTPUT_DIR
# BOUNDS, CONS_SUM (h^T1 = 1) and W0 (equal weights) are set in portfolio_utils.py
from portfolio_utils import monthly_mean_returns, BOUNDS, CONS_SUM, W0, portfolio_stats

def min_volatility(weights):
    return portfolio_stats(weights)[1] # return volatility - optimiser minimises this

# what this does: for each target return, find the portfolio with the minimum volatility
target_returns = np.linspace(monthly_mean_returns.min() * 12, monthly_mean_returns.max() * 12, 200)
frontier = []
for target in target_returns:
    cons = [
        CONS_SUM,
        {"type": "eq", "fun": lambda w, t=target: portfolio_stats(w)[0] - t}
    ]
    result = minimize(min_volatility, W0, method="SLSQP", bounds=BOUNDS, constraints=cons)
    if result.success:
        ret, vol = portfolio_stats(result.x)
        frontier.append({"annualised_return": ret, "annualised_vol": vol})
    else:
        print(f"Solve failed at target return {target:.4f}%: {result.message}")

frontier_df = pd.DataFrame(frontier)
frontier_df.to_csv(OUTPUT_DIR / "efficient_frontier.csv", index=False)
print(f"Efficient frontier: {len(frontier_df)} points written to output/efficient_frontier.csv")
