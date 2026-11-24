import numpy as np
from load_data import sections, SECTORS, ff_factors

# --- settings (one place only) ---
ALLOW_SHORT = True        # True: h unrestricted in sign (section 6.4); False: h >= 0 (section 6.5)

# --- data ---
monthly_vw_returns = sections["Average Value Weighted Returns -- Monthly"][SECTORS].copy()
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
BOUNDS   = None if ALLOW_SHORT else tuple((0, 1) for _ in range(n))
CONS_SUM = {"type": "eq", "fun": lambda w: np.sum(w) - 1}   # h^T 1 = 1
W0       = np.ones(n) / n

def portfolio_stats(w):
    """Annualised (return %, volatility %): mu(P) = h^T mu, sigma(P) = sqrt(h^T V h)."""
    return w @ monthly_mean_returns * 12, np.sqrt(w @ monthly_cov_matrix @ w * 12)

def sharpe(w, e=RISK_FREE_RATE):
    """Sharpe ratio (mu(P) - e) / sigma(P), annualised."""
    ret, vol = portfolio_stats(w)
    return (ret - e) / vol
