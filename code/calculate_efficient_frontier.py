import numpy as np
import pandas as pd
from scipy.optimize import minimize
from load_data import sections, SECTORS, OUTPUT_DIR

monthly_vw_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].copy()

mean_returns = monthly_vw_returns.mean().values
cov_matrix = monthly_vw_returns.cov().values
n = len(SECTORS)

def portfolio_stats(weights):
    # portfolio return μ(P) = h^Tμ
    ret = np.dot(weights, mean_returns) * 12 
    # portfolio volatility σ(P) = sqrt(h^TVh)
    vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights))) * np.sqrt(12)
    return ret, vol

def min_volatility(weights):
    return portfolio_stats(weights)[1] # return volatility - optimiser minimises this

# h^T1 = 1 constraint (weights sum to 1)
constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1} 

# h >= 0 constraint (no shorting)
bounds = tuple((0, 1) for _ in range(n))

#starting guess for the weights (equal allocation) - we optimise from there
w0 = np.ones(n) / n

# what this does: for each target return, find the portfolio with the minimum volatility
target_returns = np.linspace(mean_returns.min() * 12, mean_returns.max() * 12, 200)
frontier = []
for target in target_returns:
    cons = [
        constraints,
        {"type": "eq", "fun": lambda w, t=target: portfolio_stats(w)[0] - t}
    ]
    result = minimize(min_volatility, w0, method="SLSQP", bounds=bounds, constraints=cons)
    if result.success:
        ret, vol = portfolio_stats(result.x)
        frontier.append({"annualised_return": ret, "annualised_vol": vol})

frontier_df = pd.DataFrame(frontier)
frontier_df.to_csv(OUTPUT_DIR / "efficient_frontier.csv", index=False)
print(f"Efficient frontier: {len(frontier_df)} points written to output/efficient_frontier.csv")
