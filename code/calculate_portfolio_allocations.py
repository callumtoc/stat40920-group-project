import numpy as np
import pandas as pd
from scipy.optimize import minimize
from load_data import sections, SECTORS, OUTPUT_DIR

monthly_vw_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].copy()

mean_returns = monthly_vw_returns.mean().values
cov_matrix = monthly_vw_returns.cov().values
n = len(SECTORS)

def portfolio_stats(weights):
    ret = np.dot(weights, mean_returns) * 12
    vol = np.sqrt(weights @ cov_matrix @ weights) * np.sqrt(12)
    return ret, vol

def min_volatility(weights):
    return portfolio_stats(weights)[1]

def neg_sharpe(weights):
    ret, vol = portfolio_stats(weights)
    return -ret / vol

constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
bounds = tuple((0, 1) for _ in range(n))
w0 = np.ones(n) / n

portfolios = {
    "low_risk":    minimize(min_volatility, w0, method="SLSQP", bounds=bounds, constraints=constraints),
    "high_return": minimize(neg_sharpe,     w0, method="SLSQP", bounds=bounds, constraints=constraints),
}

low_ret  = portfolio_stats(portfolios["low_risk"].x)[0]
high_ret = portfolio_stats(portfolios["high_return"].x)[0]
mid_target = (low_ret + high_ret) / 2
portfolios["medium_risk"] = minimize(
    min_volatility, w0, method="SLSQP", bounds=bounds,
    constraints=[constraints, {"type": "eq", "fun": lambda w: portfolio_stats(w)[0] - mid_target}]
)

rows = []
for name, result in portfolios.items():
    ret, vol = portfolio_stats(result.x)
    row = {"portfolio": name, "annualised_return": round(ret, 4), "annualised_vol": round(vol, 4), "sharpe": round(ret / vol, 4)}
    row.update({s: round(w, 4) for s, w in zip(SECTORS, result.x)})
    rows.append(row)

allocations_df = pd.DataFrame(rows).set_index("portfolio")
allocations_df.to_csv(OUTPUT_DIR / "portfolio_allocations.csv")
print(allocations_df.to_string())
