import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.analysis.models import check_low_deviation, get_model, get_model_curves
from src.analysis.variable_preparations import bin_high_climate_variable_values, get_landcover_high_count_distribution


def create_categorybased_visual (category: str, df: pd.DataFrame, col: str, unit: str, round_decimals: int):
    
    x_col = df[col] 

    if category == "climate":
        col_label = col.replace("_", " ").title() + f" [{unit}]"

        if check_low_deviation(x_col):
            return None, None, None, "Keine ausreichende Varianz in den Daten."

        binned_df, min_bin_value, max_bin_value = bin_high_climate_variable_values(df, col)

        binned_df["rounded_bin_value"] = binned_df["bin_value"].apply(lambda x: round(x, round_decimals))

        # =========================================================================================================
        # Modellkurven generieren
        
        selected_model, selected_model_type, _ = get_model(binned_df["bin_value"], binned_df["proportion"])

        if selected_model:
            x_curve, y_curve = get_model_curves(selected_model, selected_model_type, min_bin_value, max_bin_value)
        
        # =========================================================================================================
        # Visualisierung

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=binned_df["rounded_bin_value"],
            y=binned_df["proportion"] * 100,
            mode="markers",
            marker=dict(
                color="#c77a44",
                size=6
            ),
            name="Top 20 %",
            customdata=binned_df["proportion"],
            hovertemplate=(
                "<b>High Count Distribution</b><br><br>"
                f"<b>{col.replace('_', ' ').title()}:</b> %{{x}} {unit}<br>"
                "<b>High Count Proportion:</b> %{customdata:.1%}"
                "<extra></extra>"
            )
        ))

        fig.update_layout(
            title=dict(
                text=f"High Count Distribution concerning {col.replace('_', ' ').title()}",
                x=0.5,
                xanchor="center",
                font= dict(
                    size=20
                )
            ),
            showlegend=False,
            plot_bgcolor="#fae6bb",
            paper_bgcolor="#fae6bb",
            xaxis=dict(
                title=dict(
                    text=col_label,
                    font=dict(color="#222222")
                ),
                tickfont=dict(color="#222222")
            ),
            yaxis=dict(
                gridcolor="#e4ccbe",
                title=dict(
                    text="High Species Count Proportion [%]",
                    font=dict(color="#222222")
                ),
                tickfont=dict(color="#222222")
            )
        ) 

        if selected_model:
            fig.add_trace(go.Scatter(
                x=x_curve,
                y=y_curve * 100,
                mode="lines",
                line=dict(
                    color="#c77a44",
                    width=2
                ),
                name=f"{selected_model_type.capitalize()} model",
                customdata=np.round(x_curve, round_decimals),
                hovertemplate=(
                    f"<b>{selected_model_type.capitalize()} Model</b><br><br>"
                    f"<b>{col.replace('_', ' ').title()}:</b> %{{customdata}} {unit}<br>"
                    "<b>High Species Count Proportion:</b> %{y:.1f}%"
                    "<extra></extra>"
                )
            ))

            return fig, selected_model, selected_model_type, None

        else: 
            return fig, None, None, None


    if category == "land_cover":
        col_label = "Landcover Proportion - " + col.replace("_", " ").title()

        _ , distribution_df = get_landcover_high_count_distribution(df, col)

        fig = px.bar(
            distribution_df,
            y=distribution_df.index,
            x=(distribution_df["proportion"] * 100).apply(lambda x: round(x, round_decimals)),
            orientation="h",
            color="origin",
            color_discrete_map={
                "lower": "#d92929",
                "regular": "#daa520",
                "higher": "#d92929"
            },
            title=f"High Count Distribution concerning {col.replace('_', ' ').title()}",
            text=distribution_df["proportion"] * 100,
            height=450
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            textfont=dict(
                color="#222222",
                size=12
            )
        )

        fig.update_layout(
            title=dict(
                x=0.5,
                xanchor="center",
                font= dict(
                    size=20
                )
            ),
            showlegend=False,
            plot_bgcolor="#fae6bb",
            paper_bgcolor="#fae6bb",
            xaxis=dict(
                title=None,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                title=dict(
                    text=col_label,
                    font=dict(color="#666666")
                ),
                tickfont=dict(color="#666666")
            ),
            margin=dict(
                t=40,
                b=0,
                l=0,
                r=0
            ),
            hovermode=False
        ) 

        return fig, None, None, None

        