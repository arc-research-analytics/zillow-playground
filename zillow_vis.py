import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
from PIL import Image

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

# define mapping function for super districts first
def superDistrict_mapper():

    # get URL from Open Data Portal
    url = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2021_Population/FeatureServer/20/query?where=PlanningRegion%20%3D%20'ATLANTA%20REGIONAL%20COMMISSION'&outFields=NAME,GEOID&outSR=4326&f=json"

    # define geodataframe
    gdf = gpd.read_file(url)

    initial_view_state = pdk.ViewState(
        latitude=34.207054643497315,
        longitude=-84.10535919531371, 
        zoom=9.9, 
        max_zoom=12, 
        min_zoom=8,
        pitch=0,
        bearing=0,
        height=590
    )

    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        pickable=True,
        autoHighlight=True,
        highlight_color = [255, 255, 255, 80],
        opacity=0.5,
        stroked=True,
        filled=True,
        # get_fill_color='choro_color',
        get_line_color=[0, 0, 0, 255],
        line_width_min_pixels=1
    )

    r = pdk.Deck(
        layers=geojson,
        initial_view_state=initial_view_state,
        map_provider='mapbox',
        map_style='light',
        # tooltip=tooltip
        )

    return r


# create dropdown for summary level
geography = st.radio(
    'Select geography to summarize:',
    ('County', 'Super district'),
    index=1)

st.write("Data provided via the Zestimate API")

# show map
st.pydeck_chart(superDistrict_mapper(), use_container_width=True)

image = Image.open('zillow_logo.png')


st.write("Data collected from May 1, 2023 to May 4, 2024.")








