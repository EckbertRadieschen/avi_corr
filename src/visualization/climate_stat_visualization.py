import pandas as pd
import plotly.express as px

def main_bar_chart(variable_df, top_bottom, rounding_decimals, unit):
    sort_order = top_bottom == "top" 

    variable_df = variable_df.sort_values("optimum", ascending=sort_order)
    variable_df = variable_df.tail(10)

    variable_df["text"] = variable_df["optimum"].apply(
        lambda x: f"{round(x, rounding_decimals)} {unit}"
    )

    fig = px.bar(
        variable_df,
        x="optimum",
        y="common_name",
        orientation="h",
        color_discrete_sequence=["#c77a44"],
        text="text"
    )

    fig.update_traces(
        textfont=dict(
            color="#ffffff"
        )
    )

    fig.update_xaxes(
        showticklabels=False
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(t=20, b=10),
        hovermode=False
    )

    return fig

def range_type_pie (variable, variable_df: pd.DataFrame):
    range_type_counts = variable_df["range_type"].value_counts()

    fig = px.pie(
        names=range_type_counts.index,
        values=range_type_counts.values,
        color_discrete_sequence=[
            "#E4B75C",
            "#E4422D"
        ],
        title="Distribution by Preference Range"
    )

    fig.update_traces(
        textfont=dict(
            color="#111111",
            size=16
        )
    )

    fig.update_layout(
        margin=dict(t=60, b=10),
        hovermode=False,
        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 20
            }
        }
    )

    return fig

def optimum_class_bars (variable, variable_df: pd.DataFrame):
    optimum_class_counts = variable_df["variable_preference"].value_counts(normalize=True)
    optimum_classes_df = optimum_class_counts.to_frame().reset_index()
    optimum_classes_df.columns = ["range_type", "proportion"]
    optimum_classes_df["text"] = optimum_classes_df["proportion"].apply(lambda x: f"{round(x * 100, 1)}%")

    class_order = ["very low", "low", "mid", "high", "very high"]

    fig = px.bar(
        optimum_classes_df,
        x="range_type",
        y="proportion",
        category_orders={"x": class_order},
        color_discrete_sequence=["#c77a44"],
        text="text",
        title=f"Distribution by {variable.replace('_', ' ').capitalize()} Preference"
    )

    fig.update_traces(
        textfont=dict(
            color="#ffffff"
        )
    )

    fig.update_yaxes(
        showticklabels=False
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(t=60, b=10),
        hovermode=False,
        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 20
            }
        }
    )

    return fig


def range_width_chart(variable_df, top_bottom, rounding_decimals, unit):
    sort_order = top_bottom == "top"

    variable_df = variable_df.sort_values("preference_range_width", ascending=sort_order)
    variable_df = variable_df.tail(10)

    variable_df["text"] = variable_df["preference_range_width"].apply(
        lambda x: f"{round(x, rounding_decimals)} {unit}"
    )

    fig = px.bar(
        variable_df,
        x="preference_range_width",
        y="common_name",
        orientation="h",
        color_discrete_sequence=["#c77a44"],
        text="text"
    )

    fig.update_traces(
        textfont=dict(
            color="#ffffff"
        )
    )

    fig.update_xaxes(
        showticklabels=False
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(t=20, b=10),
        hovermode=False
    )

    return fig