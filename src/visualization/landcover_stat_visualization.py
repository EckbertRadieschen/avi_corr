import pandas as pd
import plotly.express as px

def habitat_type_bar_chart(data: list):
    df = pd.DataFrame(data)

    total_count = df["count"].sum()

    df["proportion"] = df["count"] / total_count

    df["text"] = df["proportion"].apply(
            lambda x: f"{round(x * 100, 1)}%"
        )

    fig = px.bar(
        df.tail(10),
        x="proportion",
        y="type",
        orientation="h",
        color_discrete_sequence=["#c77a44"],
        text="text",
        title="Top 10 - Most Common Habitat Types"
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
        margin=dict(t=60, b=10),
        hovermode=False,
        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 20
            }
        },
        plot_bgcolor = "#fae6bb",
        paper_bgcolor="#fae6bb"
    )

    return fig

def urbanization_boxplot (data: list):
    df = pd.DataFrame(data)

    q3_pre = df["value"].quantile(0.75)
    q1_pre = df["value"].quantile(0.25)
    iqr_pre = q3_pre - q1_pre

    filter = df["value"] < q3_pre + 1.5 * iqr_pre
    df_box = df[filter].copy()

    q3 = df_box["value"].quantile(0.75)
    median = df_box["value"].median()
    q1 = df_box["value"].quantile(0.25)
    iqr = q3 - q1

    lower_whisker = df_box.loc[
        df_box["value"] > q1 - 1.5 * iqr,
        "value"
    ].min()

    upper_whisker = df_box.loc[
        df_box["value"] < q3 + 1.5 * iqr,
        "value"
    ].max()

    fig = px.box(
        df_box,
        x="value",
        color_discrete_sequence=["#c77a44"],
        title="Distribution Urbanization Tolerance"
    )

    positions = {
        "Lower-Cap": lower_whisker,
        "Q1": q1,
        "Median": median,
        "Q3": q3,
        "Upper-Cap": upper_whisker
    }

    for label, value in positions.items():
        fig.add_vline(
            x=value,
            line_dash="dash",
            line_color="#73361C",
            line_width=0.5,
            annotation_text=f"{label}: {value:.1f}",
            annotation_position="top"
        )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    fig.update_traces(hoverinfo="skip", hovertemplate=None)

    fig.update_layout(
        margin=dict(t=60, b=10),
        showlegend=False,
        hovermode=False,
        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 20
            }
        },
        plot_bgcolor = "#fae6bb",
        paper_bgcolor="#fae6bb"
    )

    return fig


def water_urbanization_bar_chart (data: list, top_bottom: str):
    df = pd.DataFrame(data)

    sort_order = top_bottom == "top"
    df = df.sort_values("value", ascending=sort_order)
    df = df.tail(10)

    df["text"] = df["value"].apply(
        lambda x: f"{round(x, 1)}%"
    )

    fig = px.bar(
        df,
        x="value",
        y="name",
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
        hovermode=False,
        plot_bgcolor = "#fae6bb",
        paper_bgcolor="#fae6bb"
    )

    return fig
