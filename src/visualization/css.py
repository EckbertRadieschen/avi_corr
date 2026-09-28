import streamlit as st

def climate_bar_css():
    st.markdown("""
    <style>
    .climate-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
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
        height: 25px;
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
        justify-content: space-between;
        margin-top: 5px;
        font-size: 11px;
        opacity: 0.55;
        color: var(--text-color);
    }
    </style>
    """, unsafe_allow_html=True)