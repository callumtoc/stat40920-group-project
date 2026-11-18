from load_data import OUTPUT_DIR
from portfolio_utils import monthly_vw_returns

correlation_matrix = monthly_vw_returns.corr()
covariance_matrix = monthly_vw_returns.cov()

# write outputs to csv, will make a heatmap and format in Excel later
correlation_matrix.round(4).to_csv(OUTPUT_DIR / "correlation_matrix.csv")
covariance_matrix.round(6).to_csv(OUTPUT_DIR / "covariance_matrix.csv")

# just to show command worked in terminal
print("Correlation matrix:")
print(correlation_matrix.round(4).to_string())
print()
print("Covariance matrix:")
print(covariance_matrix.round(6).to_string())
