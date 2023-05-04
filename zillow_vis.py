import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import conda
import os

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

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





# title








