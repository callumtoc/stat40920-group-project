import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def simulate_fund(weights, monthly_returns, rebalance_every, initial_fund=1.0):
    """Fund values F_0..F_T for target weights h; returns (T, d) -> (T+1,), or (K, T, d) -> (K, T+1)."""
    monthly_returns = np.asarray(monthly_returns, float)
    *batch_shape, n_months, n_sectors = monthly_returns.shape
    fund_values = np.empty((*batch_shape, n_months + 1))
    fund_values[..., 0] = initial_fund
    holdings = np.broadcast_to(initial_fund * weights, (*batch_shape, n_sectors)).copy()  # A_0 = F_0 h
    for m in range(1, n_months + 1):
        if rebalance_every is not None and (m - 1) % rebalance_every == 0:  # m in R: reset to targets
            holdings = fund_values[..., m - 1, None] * weights
        holdings = holdings * (1 + monthly_returns[..., m - 1, :])          # A_m = A+_{m-1} * (1 + i_m)
        fund_values[..., m] = holdings.sum(axis=-1)                         # F_m = 1^T A_m
    return fund_values


def turnover(weights, monthly_returns, rebalance_every):
    """Total fraction of the fund traded at resets, excluding the initial purchase."""
    if rebalance_every is None:
        return 0.0
    held_weights, total = weights.copy(), 0.0
    for m in range(1, len(monthly_returns) + 1):
        if (m - 1) % rebalance_every == 0 and m > 1:
            total += np.abs(held_weights - weights).sum()
            held_weights = weights.copy()
        grown = held_weights * (1 + monthly_returns[m - 1])
        held_weights = grown / grown.sum()
    return total


def backtest_metrics(fund_values, weights, monthly_returns, rebalance_every):
    """Final value, total return, annualised vol, max drawdown and turnover of one realised path."""
    fund_returns = fund_values[1:] / fund_values[:-1] - 1
    drawdowns = fund_values / np.maximum.accumulate(fund_values) - 1
    return {"Final value ($)": fund_values[-1], "Total return": fund_values[-1] / fund_values[0] - 1,
            "Annualised vol": fund_returns.std(ddof=1) * np.sqrt(12), "Max drawdown": drawdowns.min(),
            "Turnover": turnover(weights, monthly_returns, rebalance_every)}


def simulate_returns(monthly_mean_returns_decimal, monthly_cov_matrix_decimal, n_simulations, horizon_months, seed):
    """K x T x d multivariate normal monthly returns: i_m = mu + L z_m, with L L^T = V."""
    cholesky_factor = np.linalg.cholesky(monthly_cov_matrix_decimal)
    n_sectors = len(monthly_mean_returns_decimal)
    standard_normals = np.random.default_rng(seed).standard_normal((n_simulations, horizon_months, n_sectors))
    return monthly_mean_returns_decimal + standard_normals @ cholesky_factor.T


def bootstrap_returns(historical_returns, n_simulations, horizon_months, seed):
    """K x T x d returns made by resampling whole historical months with replacement."""
    historical_returns = np.asarray(historical_returns, float)
    month_index = np.random.default_rng(seed).integers(0, len(historical_returns), size=(n_simulations, horizon_months))
    return historical_returns[month_index]


def summarise(final_values, initial_fund, years=5):
    """Mean, median, percentiles, P(loss) with its standard error, and median growth p.a. of F_T."""
    p_loss = (final_values < initial_fund).mean()
    return {"Mean": final_values.mean(), "Median": np.median(final_values),
            "5th pct": np.percentile(final_values, 5), "10th pct": np.percentile(final_values, 10),
            "90th pct": np.percentile(final_values, 90), "95th pct": np.percentile(final_values, 95),
            "P(loss)": p_loss, "SE of P(loss)": np.sqrt(p_loss * (1 - p_loss) / len(final_values)),
            "Median growth p.a.": (np.median(final_values) / initial_fund) ** (1 / years) - 1}


def lognormal_approx(weights, monthly_mean_returns_decimal, monthly_cov_matrix_decimal, initial_fund, n_months):
    """Chapter 2 check: exact mean of F_n, and lognormal median, 5th/95th percentiles and P(loss)."""
    mu_P = weights @ monthly_mean_returns_decimal
    sigma_P = np.sqrt(weights @ monthly_cov_matrix_decimal @ weights)
    sigma2_delta = np.log(1 + (sigma_P / (1 + mu_P)) ** 2)  # sigma_delta^2 = ln(1 + CV^2)
    mu_delta = np.log(1 + mu_P) - sigma2_delta / 2
    log_mean, log_sd = n_months * mu_delta, np.sqrt(n_months * sigma2_delta)
    return {"Mean": initial_fund * (1 + mu_P) ** n_months, "Median": initial_fund * np.exp(log_mean),
            "5th pct": initial_fund * np.exp(log_mean + norm.ppf(0.05) * log_sd),
            "95th pct": initial_fund * np.exp(log_mean + norm.ppf(0.95) * log_sd),
            "P(loss)": norm.cdf(-log_mean / log_sd)}


def fan_chart(fund_values, title, ax, initial_fund):
    """Fan chart of simulated paths: 90/80/50% bands, median and the initial fund line."""
    months = np.arange(fund_values.shape[1])
    for lo, hi, alpha, label in [(5, 95, 0.15, "90% band"), (10, 90, 0.25, "80% band"), (25, 75, 0.4, "50% band")]:
        ax.fill_between(months, np.percentile(fund_values, lo, axis=0), np.percentile(fund_values, hi, axis=0),
                        alpha=alpha, color="C0", lw=0, label=label)
    ax.plot(months, np.median(fund_values, axis=0), color="C0", lw=2, label="Median")
    ax.axhline(initial_fund, color="grey", ls="--", lw=1)
    ax.set_title(title); ax.set_xlabel("Month"); ax.set_xticks(range(0, 61, 12)); ax.grid(alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}m"))
