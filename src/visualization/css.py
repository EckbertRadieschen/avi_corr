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
            border: 3px double #880000
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
            width: 100px;
            aspect-ratio: 1;
            border: 2px solid #880000;
            border-radius: 50%;
            background: white;

            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .info-content {
            font-size: 15px;
            font-weight: bold;
            color: #17384a;
            padding: 15px;
        }
    </style>
    """, unsafe_allow_html=True)


def water_need_css():
    st.markdown("""
        <style>
        .water-gauge {
            position: relative;
            width: 100px;
            aspect-ratio: 1;
            border: 2px solid #880000;
            border-radius: 50%;
            overflow: hidden;
            background: white
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
            font-size: 15px;
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