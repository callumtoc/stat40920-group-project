import pandas as pd
from scipy.optimize import minimize
from load_data import SECTORS, OUTPUT_DIR
# BOUNDS, CONS_SUM (h^T1 = 1), W0 (equal weights) and sharpe (which uses RISK_FREE_RATE) are set in
# portfolio_utils.py, which builds monthly_mean_returns and monthly_cov_matrix from monthly_vw_returns
from portfolio_utils import bounds_for, CONS_SUM, W0, portfolio_stats, sharpe, RISK_FREE_RATE

def min_volatility(weights):
    return portfolio_stats(weights)[1]

def neg_sharpe(weights):
    return -sharpe(weights)  # scipy only minimises, so minimise -Sharpe to maximise Sharpe

portfolios = {
    "low_risk":  minimize(min_volatility, W0, method="SLSQP", bounds=bounds_for("low_risk"), constraints=CONS_SUM),
    "high_risk": minimize(neg_sharpe,     W0, method="SLSQP", bounds=bounds_for("high_risk"), constraints=CONS_SUM),
}

low_ret  = portfolio_stats(portfolios["low_risk"].x)[0]
high_ret = portfolio_stats(portfolios["high_risk"].x)[0]
mid_target = (low_ret + high_ret) / 2
portfolios["medium_risk"] = minimize(
    min_volatility, W0, method="SLSQP", bounds=bounds_for("medium_risk"),
    constraints=[CONS_SUM, {"type": "eq", "fun": lambda w: portfolio_stats(w)[0] - mid_target}]
)

assert all(result.success for result in portfolios.values()), "an optimisation failed - check WEIGHT_LIMITS"

rows = []
for name, result in portfolios.items():
    ret, vol = portfolio_stats(result.x)
    row = {"portfolio": name, "annualised_return": ret, "annualised_vol": vol, "sharpe": sharpe(result.x), "risk_free_rate": RISK_FREE_RATE}
    row.update({s: w for s, w in zip(SECTORS, result.x)})
    rows.append(row)

allocations_df = pd.DataFrame(rows).set_index("portfolio")
allocations_df.to_csv(OUTPUT_DIR / "portfolio_allocations.csv")
print(allocations_df.to_string())
print(f"\nRisk-free rate used (annual %): {RISK_FREE_RATE:.4f}")
