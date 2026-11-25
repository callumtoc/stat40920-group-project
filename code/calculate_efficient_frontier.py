import numpy as np
import pandas as pd
from scipy.optimize import minimize, linprog
from load_data import OUTPUT_DIR
# CONS_SUM (h^T1 = 1), W0 (equal weights), bounds_for and WEIGHT_LIMITS are set in portfolio_utils.py
from portfolio_utils import monthly_mean_returns, CONS_SUM, W0, bounds_for, portfolio_stats, WEIGHT_LIMITS, n

def min_volatility(weights):
    return portfolio_stats(weights)[1]  # return volatility - optimiser minimises this

# one frontier per portfolio's constraint set, so each portfolio can be shown on its own frontier
frontier = []
for portfolio in WEIGHT_LIMITS:
    bounds = bounds_for(portfolio)

    # efficient (upper) part only: from the minimum-variance return up to the highest achievable return
    min_var = minimize(min_volatility, W0, method="SLSQP", bounds=bounds, constraints=CONS_SUM)
    max_ret = linprog(-monthly_mean_returns, A_eq=np.ones((1, n)), b_eq=[1], bounds=bounds)  # max h^T mu
    lowest, highest = portfolio_stats(min_var.x)[0], portfolio_stats(max_ret.x)[0]

    for target in np.linspace(lowest, highest, 100):
        cons = [CONS_SUM, {"type": "eq", "fun": lambda w, t=target: portfolio_stats(w)[0] - t}]
        result = minimize(min_volatility, W0, method="SLSQP", bounds=bounds, constraints=cons)
        if result.success:
            ret, vol = portfolio_stats(result.x)
            frontier.append({"constraint_set": portfolio, "annualised_return": ret, "annualised_vol": vol})
        else:
            print(f"{portfolio}: solve failed at target return {target:.4f}%: {result.message}")

frontier_df = pd.DataFrame(frontier)
frontier_df.to_csv(OUTPUT_DIR / "efficient_frontier.csv", index=False)
print(f"Efficient frontiers: {len(frontier_df)} points written to output/efficient_frontier.csv")