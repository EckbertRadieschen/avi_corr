import plotly.graph_objects as go

def plot_species_usa_map(species_grid):
    features = species_grid["features"]
    locations = []
    values = []

    for feature in features:
        values.append(feature["properties"]["value"])
        locations.append(feature["id"])

    colorscale_map = [
        [0.00, "#FFFFFF"],
        [0.10, "#FFF0B3"],
        [0.25, "#FFB347"],
        [0.55, "#FF6B1A"],
        [0.75, "#D7191C"],
        [1.00, "#8B0000"]
    ]

    fig = go.Figure(
        go.Choroplethmap(
            geojson=species_grid,
            locations=locations,
            z=values,
            featureidkey="id",
            colorscale=colorscale_map,
            zmin=0,
            zmax=1,
            marker={"line": {"width": 0}},
            colorbar={
                "title": {"text": "High-count ratio"},
                "tickvals": [0, 0.25, 0.5, 0.75, 1],
                "ticktext": ["0", "0.25", "0.5", "0.75", "1"]
            },
            hoverinfo="skip"
        )
    )

    fig.update_traces(
        showscale=False
    )

    fig.update_layout(
        map={
            "style": "carto-positron",
            "center": {"lat": 38.0, "lon": -98.5},
            "zoom": 2.6
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=270
    )

    return fig

