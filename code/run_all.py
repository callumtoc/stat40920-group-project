import os
import subprocess
import sys
from pathlib import Path

code_dir = Path(__file__).resolve().parent

# dependency order: the plot reads the frontier and allocation csvs, and the forecast reads the allocation csv
scripts = [
    "generate_summary_statistics.py",
    "build_correlation_covariance.py",
    "calculate_portfolio_allocations.py",
    "calculate_efficient_frontier.py",
    "plot_efficient_frontier.py",
    "run_forecast.py",
    "export_to_excel.py",   # last: collects every csv and chart above into output/results.xlsx
    "run_historical.py",
]

# non-interactive matplotlib backend, so plt.show() in the plot script doesn't block the run
os.environ["MPLBACKEND"] = "Agg"

for script in scripts:
    print(f"\n=== {script} ===", flush=True)  # flush so the header prints before the script's own output
    subprocess.run([sys.executable, script], check=True, cwd=code_dir)  # a failure stops the run

print("\nAll scripts completed.")
