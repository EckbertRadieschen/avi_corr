import pandas as pd

CORRELATIONS_PSP_URL = "data/processed/correlations_psp_regular.csv"
CORRELATIONS_QUAD_URL = "data/processed/correlations_quad_regular.csv"

df_psp = pd.read_csv(CORRELATIONS_PSP_URL, encoding="utf-8")
df_quad = pd.read_csv(CORRELATIONS_QUAD_URL, encoding="utf-8")

df_psp = df_psp.sort_values("spearman_rho")

species_list = list(set(list(df_psp["species"].unique()) + list(df_quad["species"].unique())))

for species in species_list[:5]:
    species_df = df_psp.copy()
    species_filter = species_df["species"] == species
    species_df = species_df[species_filter].sort_values("spearman_rho", ascending=False)

    print(f"Correlations for species {species}\n")
    
    for _, row in species_df.iterrows():
        print(
            f"Indikator: {row['variable']}_{row['indicator']} | "
            f"Spearman ρ: {row['spearman_rho']:.3f} | "
            f"n: {row['n']}"
        )

    species_df = df_quad.copy()
    species_filter = species_df["species"] == species
    species_df = species_df[species_filter].sort_values("rsquared", ascending=False)

    for _, row in species_df.iterrows():
        sign = "Maximum" if str(row["beta2"])[0] == "-" else "Minimum"
        print(
            f"Indikator: {row['variable']}_{row['indicator']} | "
            f"R²: {row['rsquared']:.3f} | "
            f"Min/Max: {sign} | "
            f"Optimum: {row['optimum']:.3f} | "
            f"n: {row['n']}"
        )

    print("=" * 60)