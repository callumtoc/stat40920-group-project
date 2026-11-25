import pandas as pd
from load_data import OUTPUT_DIR
from portfolio_utils import BACKTEST_START, BACKTEST_END, PORTFOLIO_LABELS

# Decision rule for each portfolio's rebalancing frequency (uses run_forecast.py outputs):
#   1. Only Monthly, Quarterly or Annual are allowed (the brief asks for one of these; "Never" lets weights drift).
#   2. Take the frequency with the highest backtest final value.
#   3. Keep it only if it beats Annual (the least-trading option) by more than MATERIAL and its
#      max drawdown is no worse; otherwise choose Annual, since the extra trading isn't worth it.
#   4. Show the simulated (Monte Carlo) median and P(loss) as a check that nothing contradicts the choice.
MATERIAL = 0.01   # 1% of final value
ALLOWED = ["Monthly", "Quarterly", "Annual"]

backtest = pd.read_csv(OUTPUT_DIR / "backtest_rebalancing.csv")
simulated = pd.read_csv(OUTPUT_DIR / "mc_rebalancing_comparison.csv")

rows = []
for portfolio, bt in backtest[backtest["Rebalancing"].isin(ALLOWED)].groupby("Portfolio", sort=False):
    bt = bt.set_index("Rebalancing")
    best, annual = bt["Final value ($)"].idxmax(), bt.loc["Annual"]
    gain = bt.loc[best, "Final value ($)"] / annual["Final value ($)"] - 1
    worth_it = gain > MATERIAL and bt.loc[best, "Max drawdown"] >= annual["Max drawdown"]
    choice = best if worth_it else "Annual"
    sim = simulated[(simulated["Portfolio"] == portfolio) & (simulated["Rebalancing"] == choice)].iloc[0]
    rows.append({
        "Portfolio": portfolio,
        "Best in backtest": best,
        "Gain vs annual": f"{gain:+.1%}",
        "CHOICE": choice,
        "Final value": f"${bt.loc[choice, 'Final value ($)'] / 1e6:.3f}m",
        "Max drawdown": f"{bt.loc[choice, 'Max drawdown']:.1%}",
        "Turnover": f"{bt.loc[choice, 'Turnover']:.2f}x",
        "Sim. median": f"${sim['Median'] / 1e6:.3f}m",
        "Sim. P(loss)": f"{sim['P(loss)']:.1%}",
    })

print(f"\nRebalancing decision (backtest {BACKTEST_START} to {BACKTEST_END}; "
      f"switch from Annual only if > {MATERIAL:.0%} better with no worse drawdown)\n")
print(pd.DataFrame(rows).set_index("Portfolio").to_string())
letters = {label: letter for letter, label in PORTFOLIO_LABELS.items()}   # "Portfolio A (Low Risk)" -> "A"
choices = {letters[r["Portfolio"]]: r["CHOICE"] for r in rows}
months = {"Monthly": 1, "Quarterly": 3, "Annual": 12}
print(f"\nSet in portfolio_utils.py:  REBALANCE_MONTHS = {{{', '.join(f'{k!r}: {months[v]}' for k, v in choices.items())}}}")