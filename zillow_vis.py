import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import plotly.express as px

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
</style>
""",
    unsafe_allow_html=True,
)

# title
st.title('Zillow Zestimate 30-Day Change')

# create dropdown for summary level
geography = st.radio(
    'Select geography to visualize:',
    ('County', 'Super district'))





# title








