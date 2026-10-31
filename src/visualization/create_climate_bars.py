import streamlit as st
from pathlib import Path
import base64

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
ICON_DIR = ASSETS_DIR / "climate_icons"

def climate_bar(
    name: str,
    global_min: float,
    global_max: float,
    relevance_range: list[float],
    preference_range: list[float] | None = None,
    optimum: float | None = None,
    unit: str = "",
    decimals: int = 1,
):
    global_range = global_max - global_min
    relevant_min, relevant_max = relevance_range

    def position(value):
        return 100 * (value - global_min) / global_range

    def width(start, end):
        return position(end) - position(start)

    def format_value(value):
        return f"{value:.{decimals}f}{unit}"

    rel_left = position(relevant_min)
    rel_width = width(relevant_min, relevant_max)

    relevant_html = (
        f'<div class="climate-relevant" '
        f'style="left:{rel_left:.3f}%; '
        f'width:{rel_width:.3f}%;" '
        f'title="Relevant Range: '
        f'{format_value(relevant_min)} - '
        f'{format_value(relevant_max)}">'
        f'</div>'
    )

    pref_html = (
        '<div class="climate-preference missing"></div>'
    )

    if preference_range is not None:
        preference_min, preference_max = preference_range

        pref_left = position(preference_min)
        pref_width = width(preference_min, preference_max)

        pref_html = (
            f'<div class="climate-preference" '
            f'style="left:{pref_left:.3f}%; '
            f'width:{pref_width:.3f}%;" '
            f'title="Preference: '
            f'{format_value(preference_min)} - '
            f'{format_value(preference_max)}">'
            f'</div>'
        )

    optimum_html = (
        '<div class="climate-optimum missing"></div>'
    )

    if optimum is not None:
        opt_pos = position(optimum)

        optimum_html = (
            f'<div class="climate-optimum" '
            f'style="left:{opt_pos:.3f}%;" '
            f'title="Optimum: '
            f'{format_value(optimum)}">'
            f'</div>'
        )

    gmin = format_value(global_min)
    gmax = format_value(global_max)

    icon_path = ICON_DIR / f"{name}.png"
    icon_title = name.replace("_", " ").title()

    if icon_path.is_file():
        encoded = base64.b64encode(
            icon_path.read_bytes()
        ).decode("ascii")

    climate_symbol_html = (
        f'<img class="climate-icon" '
        f'src="data:image/png;base64,{encoded}" '
        f'title="{icon_title}" '
        f'alt="{icon_title}">'
    )

    st.markdown(
        f"""
        <div class="climate-item">
            {climate_symbol_html}
            <div class="climate-bar-holder">
                <div class="climate-bar">
                    {relevant_html}
                    {pref_html}
                    {optimum_html}
                </div>
                <div class="climate-scale">
                    <span>{gmin}</span>
                    <span>{gmax}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )