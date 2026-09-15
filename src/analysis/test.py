import pandas as pd

df = pd.read_csv("avi_corr_correlations.csv")


result = df[df["spearman_rho"].abs() >= 0.3].sort_values("spearman_rho")

for _, row in result.iterrows():
    print(
        f"Vogelart: {row['species']} | "
        f"Spearman ρ: {row['spearman_rho']:.3f} | "
        f"n: {row['n']}"
    )

