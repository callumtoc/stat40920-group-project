import numpy as np
from load_data import sections, SECTORS, ff_factors

# --- settings (one place only) ---
ESTIMATION_START, ESTIMATION_END = "1970-01", "2025-12"   # full calendar years in which all 10 sectors have data

# per-sector weight limits (min, max) for each portfolio: short selling allowed only as risk appetite rises
WEIGHT_LIMITS = {
    "low_risk":    (0.00, 0.30),   # A: long-only (section 6.5), max 30% in any sector
    "medium_risk": (-0.10, 0.30),  # B: limited short selling, max 10% short in any sector
    "high_risk":   (-0.20, 0.40),  # C: short selling within limits (section 6.4, bounded)
}

# forecast and rebalancing (simulation.py, run_forecast.py, notebooks/forecast_and_rebalancing.ipynb)
SEED = 40920                # same seed as Nathan's run, so results are repeatable
N_SIMULATIONS = 10_000      # K: number of simulated five-year paths
HORIZON_MONTHS = 60         # T
INITIAL_FUND = 1_000_000    # F0 ($)
REBALANCE_MONTHS = {"A": 12, "B": 12, "C": 12}   # months between resets for the forecast; None = never; group to finalise per portfolio
REBALANCE_FREQUENCIES = {"Monthly": 1, "Quarterly": 3, "Annual": 12, "Never": None}   # compared in the backtest
BACKTEST_START, BACKTEST_END = "2021-01", "2025-12"
PORTFOLIO_KEYS = {"A": "low_risk", "B": "medium_risk", "C": "high_risk"}
PORTFOLIO_LABELS = {"A": "Portfolio A (Low Risk)", "B": "Portfolio B (Medium Risk)", "C": "Portfolio C (High Risk)"}

# --- data ---
monthly_vw_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].loc[ESTIMATION_START:ESTIMATION_END].copy()
assert monthly_vw_returns.notna().all().all(), "missing returns inside the estimation window"
monthly_mean_returns = monthly_vw_returns.mean().values   # monthly %
monthly_cov_matrix   = monthly_vw_returns.cov().values    # monthly %^2
n = len(SECTORS)

# --- risk-free rate e ---
# average one-month T-bill return over the SAME months as our sector data, annualised x12
# (x12 matches how portfolio_stats annualises returns)
rf_monthly = ff_factors["RF"].reindex(monthly_vw_returns.index)
assert rf_monthly.notna().all(), "RF missing for some months - check both raw files cover the same dates"
RISK_FREE_RATE = rf_monthly.mean() * 12   # annual %

# --- optimiser settings ---
CONS_SUM = {"type": "eq", "fun": lambda w: np.sum(w) - 1}   # h^T 1 = 1
W0       = np.ones(n) / n

def bounds_for(portfolio):
    """Per-sector (min, max) weight bounds for one portfolio, in the form scipy's minimize expects."""
    lower, upper = WEIGHT_LIMITS[portfolio]
    return tuple((lower, upper) for _ in range(n))

def portfolio_stats(w):
    """Annualised (return %, volatility %): mu(P) = h^T mu, sigma(P) = sqrt(h^T V h)."""
    return w @ monthly_mean_returns * 12, np.sqrt(w @ monthly_cov_matrix @ w * 12)

def sharpe(w, e=RISK_FREE_RATE):
    """Sharpe ratio (mu(P) - e) / sigma(P), annualised."""
    ret, vol = portfolio_stats(w)
    return (ret - e) / vol
