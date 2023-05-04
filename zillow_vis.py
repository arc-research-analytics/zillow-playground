import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import geopandas as gpd

# hide sidebar
st.set_page_config(
    initial_sidebar_state="collapsed",
    layout="wide",
    )

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    .reportview-container .main footer {visibility: hidden;}    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    section.main > div:has(~ footer ) {
    padding-bottom: 5px;}
    div.block-container{padding-top:1.5rem;}
</style>
""",
    unsafe_allow_html=True,
)

# # title
# st.title('May 30-Day Zestimate Change')

# create dropdown for summary level
geography = st.radio(
    'Select geography to summarize:',
    ('County', 'Super district'),
    index=1)

st.write("Data provided via the Zestimate API")


st.write("Data collected from May 1, 2023 to May 4, 2024.")








