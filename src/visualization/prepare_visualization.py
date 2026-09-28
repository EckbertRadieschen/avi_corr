import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from patsy import dmatrix

from analysis.variable_preparations import bin_high_climate_variable_values, get_landcover_high_count_distribution

def check_low_deviation (x: pd.Series):
    mean = x.mean()
    std = x.std()
    lower = mean - 0.5 * std
    upper = mean + 0.5 * std

    sigma_counter = 0

    for value in x:
        if lower <= value <= upper:
            sigma_counter += 1

    return sigma_counter / len(x) > 0.6

def get_model_optimum(model, model_type, x_min, x_max):
    
    if model_type == "linear":
        slope = model.params[1]

        if np.isclose(slope, 0):
            return None

        if slope > 0:
            return x_max
        
        else:
            return x_min

    elif model_type == "quadratic":
        b = model.params["x"]
        c = model.params["x2"]

        if c > 0 or np.isclose(c, 0):
            return None

        optimum = -b / (2 * c)

        if x_min <= optimum <= x_max:
            return optimum

        return None

    elif model_type == "cubic":
        b = model.params["x"]
        c = model.params["x2"]
        d = model.params["x3"]

        if np.isclose(d, 0):
            return None

        # Ableitung: y' = 3*d*x² + 2*c*x + b = 0

        roots = np.roots([3 * d, 2 * c, b])

        candidates = [
            x for x in roots 
            if (not np.isreal(x)) and (x_min <= x <= x_max)
        ]

        if not candidates:
            return None

        X_candidates = np.array([
            [1, x, x**2, x**3]
            for x in candidates
        ])

        predictions = model.predict(X_candidates)
        optimum = candidates[np.argmax(predictions)]

        return optimum

    elif model_type == "spline":

        x_values = np.linspace(x_min, x_max, 1000)

        X_spline = dmatrix(
            "bs(x, df=6, degree=3, include_intercept=False)",
            {"x": x_values},
            return_type="dataframe"
        )

        predictions = model.predict(X_spline)
        optimum = x_values[np.argmax(predictions)]

        return optimum


def get_model (x_column: pd.Series, y_column: pd.Series, r2_threshold=0.7, aic_threshold=4):
    X = x_column.values
    y = y_column.values

    x_min = x_column.min()
    x_max = x_column.max()

    # ================================================
    # Modellberechnungen

    X_linear = sm.add_constant(X)
    linear_model = sm.OLS(y, X_linear).fit()
    optimum_linear = get_model_optimum(linear_model, "linear", x_min, x_max)
    
    X_quadratic = pd.DataFrame({
        "x": X,
        "x2": X ** 2
    })
    X_quadratic = sm.add_constant(X_quadratic)
    quadratic_model = sm.OLS(y, X_quadratic).fit()
    optimum_quadratic = get_model_optimum(quadratic_model, "quadratic", x_min, x_max)


    X_cubic = pd.DataFrame({
        "x": X,
        "x2": X ** 2,
        "x3": X ** 3
    })
    X_cubic = sm.add_constant(X_cubic)
    cubic_model = sm.OLS(y, X_cubic).fit()
    optimum_cubic = get_model_optimum(cubic_model, "cubic", x_min, x_max)
    
    X_spline = dmatrix(
        "bs(x, df=6, degree=3, include_intercept=False)",
        {"x": X},
        return_type="dataframe"
    )
    spline_model = sm.OLS(y, X_spline).fit()
    optimum_spline = get_model_optimum(spline_model, "spline", x_min, x_max)


    # ===========================================================
    # Modellvergleich

    if linear_model.rsquared >= r2_threshold:
        selected_model = linear_model 
        model_type = "linear"
        optimum = optimum_linear

    elif (
        quadratic_model.rsquared >= r2_threshold
        and linear_model.aic - quadratic_model.aic >= aic_threshold
        and optimum_quadratic is not None
    ):
        selected_model = quadratic_model 
        model_type = "quadratic"
        optimum = optimum_quadratic
    
    elif (
        cubic_model.rsquared >= r2_threshold
        and quadratic_model.aic - cubic_model.aic >= aic_threshold
        and optimum_cubic is not None
    ):
        selected_model = cubic_model
        model_type = "cubic"
        optimum = optimum_cubic

    elif (spline_model.rsquared >= 0.5):
        selected_model = spline_model
        model_type = "spline"
        optimum = optimum_spline

    else:
        selected_model = None

    if selected_model:
        return selected_model, model_type, optimum

    else:
        return None, None, None

def get_model_curves(model, model_type, min_value, max_value):
    x_curve = np.linspace(
        min_value,
        max_value,
        200
    )

    if model_type == "linear":
        X_curve = sm.add_constant(x_curve)
        y_curve = model.predict(X_curve)

    elif model_type == "quadratic":
        X_curve = pd.DataFrame({
            "x": x_curve,
            "x2": x_curve ** 2
        })
        X_curve = sm.add_constant(X_curve)
        y_curve = model.predict(X_curve)


    elif model_type == "cubic":
        X_curve = pd.DataFrame({
            "x": x_curve,
            "x2": x_curve ** 2,
            "x3": x_curve ** 3
        })
        X_curve = sm.add_constant(X_curve)
        y_curve = model.predict(X_curve)

    elif model_type == "spline":
        X_curve = dmatrix(
            "bs(x, df=6, degree=3, include_intercept=False)",
            {"x": x_curve},
            return_type="dataframe"
        )
        y_curve = model.predict(X_curve)

    return x_curve, y_curve


def create_categorybased_visual (category: str, df: pd.DataFrame, col: str):
    
    x_col = df[col]

    if category == "climate":
        if check_low_deviation(x_col):
            return "Keine ausreichende Varianz in den Daten."

        binned_df, min_bin_value, max_bin_value = bin_high_climate_variable_values(df, col)

        # =========================================================================================================
        # Modellkurven generieren
        
        selected_model, selected_model_type, optimum = get_model(binned_df["bin_value"], binned_df["proportion"])

        if selected_model:
            x_curve, y_curve = get_model_curves(selected_model, selected_model_type, min_bin_value, max_bin_value)
        
        # ===================================================================
        # Visualisierung

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=binned_df["bin_value"],
            y=binned_df["proportion"],
            mode="markers",
            name="Top 20 %"
        ))

        fig.update_layout(
            xaxis_title=col,
            yaxis_title="Species count",
        )

        if selected_model:
            fig.add_trace(go.Scatter(
                x=x_curve,
                y=y_curve,
                mode="lines",
                name=f"{selected_model_type.capitalize()} model"
            ))

            return fig, selected_model_type

        else: 
            return fig, "No model found"


    if category == "land_cover":
        _ , distribution_df = get_landcover_high_count_distribution(df, col)

        return px.bar(
            distribution_df,
            x=distribution_df.index,
            y="proportion",
            color="origin",
            color_discrete_map={
                "lower": "#daa520",
                "regular": "#d92929",
                "higher": "#daa520"
            }
        )




        