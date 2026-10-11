import pandas as pd
import plotly.express as px

def habitat_type_bar_chart(data: list):
    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x="count",
        y="type"
    )

    return fig

def urbanization_boxplot (data: list):
    df = pd.DataFrame(data)

    fig = px.box(
        df,
        x="value"
    )

    return fig


def water_urbanization_bar_chart (data: list, top_bottom: str):
    df = pd.DataFrame(data)

    sort_order = top_bottom == "top"
    df = df.sort_values("value", ascending=sort_order)
    df = df.tail(10)

    fig = px.bar(
        df,
        x="value",
        y="name"
    )

    return fig
