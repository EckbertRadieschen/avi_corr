import streamlit as st

def treemap_css():
    st.markdown("""
    <style>
        .remainder {
            display: flex
        }

        .box {
            display: flex;
            justify-items: center;
            align-items: center
        }
        
        .even {
            flex-direction: row
        }

        .odd {
            flex-direction: column
        }

        .treemap {
            flex: 1;
            border: 3px double #880000;
            margin-left: 10px
        }

        .box-icon {
            margin: 0 auto;
            aspect-ratio: 1 / 1;
            height: 50%;
            width: auto
        }

    </style>
    """, unsafe_allow_html=True)

def urbanization_css():
    st.markdown("""
    <style>
        .info-circle {
            width: 85px;
            aspect-ratio: 1;
            border: 2px solid #880000;
            border-radius: 50%;
            background: #b5b5b5;

            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .info-content {
            font-size: 14px;
            font-weight: bold;
            color: #17384a
        }
    </style>
    """, unsafe_allow_html=True)


def water_need_css():
    st.markdown("""
        <style>
        .water-gauge {
            position: relative;
            width: 85px;
            aspect-ratio: 1;
            border: 2px solid #880000;
            border-radius: 50%;
            overflow: hidden;
            background: #e4f5f5
        }

        .water-fill {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: var(--water);
            background: linear-gradient(
                180deg,
                #38b9e8,
                #0876b5
            )
        }

        .water-wave {
            position: absolute;
            top: -12px;
            left: 0;
            width: 100%;
            height: 24px
        }

        .water-wave path {
            fill: #38b9e8
        }

        .water-value {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: bold;
            color: #17384a;
            z-index: 2
        }

        </style>
    """, unsafe_allow_html=True
)
    
def climate_bar_css ():
    st.markdown("""
        <style>
        .climate-item {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 0 0 22px 0;
            font-family: inherit;
        }
    
        .climate-icon {
            display: block;
            width: 32px;
            height: 32px;
            object-fit: contain;
            flex: 0 0 32px;
        }
    
        .climate-bar-holder {
            flex: 1;
            min-width: 0
        }
    
        .climate-bar {
            position: relative;
            height: 20px;
            width: 100%;
            border-radius: 250px;
            background: linear-gradient(
                to bottom,
                #ddd6ca 0%,
                #d3cbbf 15%,
                #c9c0b3 50%,
                #d3cbbf 85%,
                #ddd6ca 100%
            );
            box-shadow:
                inset 0 2px 4px rgba(0,0,0,0.45),
                0 1px 1px rgba(255,255,255,0.08);
            overflow: hidden;
        }
    
        .climate-relevant {
            position: absolute;
            top: 0.5px;
            bottom: 0.5px;
            border-radius: 250px;
            background: linear-gradient(
                to bottom,
                #f5ab38 0%,
                #f7b962 15%,
                #f9c890 50%,
                #f7b962 85%,
                #f5ab38 100%
            );
            box-shadow:
                inset 0 2px 2px rgba(255,255,255,0.22),
                inset 0 -2px 3px rgba(0,0,0,0.2);
        }
    
        .climate-preference {
            position: absolute;
            top: 0.5px;
            bottom: 0.5px;
            border-radius: 250px;
            background: linear-gradient(
                to bottom,
                #942016 0%,
                #c23527 15%,
                #f04632 50%,
                #c23527 85%,
                #942016 100%
            );
            box-shadow:
                inset 0 1px 2px rgba(255,255,255,0.55),
                0 0 5px rgba(115,210,255,0.35);
            z-index: 2;
        }
    
        .climate-optimum {
            position: absolute;
            width: 0;
            top: -2px;
            bottom: 2px;
            background: transparent;
            height: 95%; 
            border-left: 1.5px dashed #444444;
            transform: translateX(-50%);
            z-index: 3;
        }
    
        .missing {
            opacity: 0 !important;
        }
    
        .climate-scale {
            display: flex;
            width: 100%;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 11px;
            opacity: 0.55;
            color: var(--text-color);
        }
        </style>
        """, unsafe_allow_html=True)

def bird_size_css ():
    gender_button_display = "None" if st.session_state["bird_gender"] == "both" else "block"

    st.markdown(f"""
        <style>
        .visual_holder {{
            display: flex; 
            flex-direction: row;
            width: 90%;
            align-items: flex-end;
            justify-content: space-between;
        }}

        [data-testid="stElementContainer"]:has(.visual_holder) {{
            position: absolute;
            z-index: 0;
            top: 50px
        }}

        [data-testid="stLayoutWrapper"]:has(.measurements_box) {{
            position: absolute;
            z-index: 10;
            width: 30%;
            top: -100px
        }}

        [data-testid="stElementContainer"]:has(#measurements) {{
            margin-top: -5px
        }}

        .st-key-measurements_header {{
            display: flex;
            flex-flow: row nowrap;
            justify-content: center
        }}

        .st-key-measurements_header [data-testid="stMarkdownContainer"] {{
            margin: 0
        }}

        .st-key-measurements_header h3 {{
            margin: 0;
            padding: 0 0 5px 0;
        }}

        .st-key-male_button button, .st-key-female_button button{{
            width: 30px;
            height: 30px;
            border: 1px solid, #880000;
            border-radius: 50%;
            padding: 0 !important;
            display: {gender_button_display}
        }}

        .st-key-male_button p, .st-key-female_button p {{
            font-size: 12px;
            font-weight: bold
        }}

        .measure_title, .measure_value {{
            display: flex;
            flex-flow: column nowrap
        }}

        .measure_title span {{
            font-size: 12px;
            font-weight: bold
        }}

        .measure_value p {{
            font-size: 12px
        }}

        .measurements {{
            display: flex;
            flex-flow: row nowrap;
            gap: 10px
        }}

        </style>
        """, unsafe_allow_html=True)


def info_hover_css ():
    st.markdown("""
        <style>
            .info_hover_holder {
                display: flex;
                border: 1px solid #c0bdae;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                align-items: center;
                justify-content: center;
                color: #c0bdae;
                font-size: 16px;
                font-weight: bold;
                position: absolute;
                z-index: 100
            }

            .hover_element {
                display: flex;
                flex-flow: column nowrap;
                position: absolute;
                z-index: 100;
                background-color: #ebd18d;
                border: 1px solid #880000;
                border-radius: 10px;
                opacity: 0;
                width: 25px;
                height: 25px;
                overflow: hidden;
                padding: 10px;
            }

            .hover_element:hover {
                opacity: 1;
                width: fit-content !important;
                height: fit-content !important
            }

            .hover_element h3 {
                padding: 0 0 3px 0 !important;
                margin: -15px 0 0 0
            }
            
            .hover_element h3 span {
                font-size: 12px
            }

            .hover_line {
                font-size: 11px
            }

            .st-key-habitat_container .hover_element,
            .st-key-habitat_container .info_hover_holder {
                top: -33px;
                left: 15px
            }

            .st-key-water_visual .hover_element,
            .st-key-water_visual .info_hover_holder {
                top: -28px !important;
                left: 0px !important;
                width: 15px; 
                height: 15px;
                font-size: 12px
            }

            .st-key-water_visual .hover_element:hover {
                width: 235px !important;
                height: 92px !important
            }

            .st-key-urbanization_visual .hover_element,
            .st-key-urbanization_visual .info_hover_holder {
                top: -39px !important;
                left: 0px !important;
                width: 15px; 
                height: 15px;
                font-size: 12px
            }

            .st-key-urbanization_visual .hover_element:hover {
                width: 235px !important;
                height: 179px !important
            }

            .st-key-map_container_holder .hover_element,
            .st-key-map_container_holder .info_hover_holder {
                top: -28px;
                left: 20px
            }

            .st-key-bars_container .hover_element,
            .st-key-bars_container .info_hover_holder {
                top: -42px;
                left: 6px;
            }
            
            

        </style>
        """, unsafe_allow_html=True)


def main_css():
    treemap_css()
    urbanization_css()
    water_need_css()
    climate_bar_css()
    info_hover_css()