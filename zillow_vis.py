import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
from PIL import Image
import os

os.environ['CACHE_ON_STARTUP'] = 'True'


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
    div.block-container{
        padding-top:1.5rem;
        padding-left:1.5rem;
        padding-right:1.5rem;
        }
    div.stActionButton{visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# data loadewr
@st.cache_data
def data_loader():

    # super districts first
    df_SD = pd.read_csv('superDistrict_final2.csv')

    url = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2021_Population/FeatureServer/20/query?where=PlanningRegion%20%3D%20'ATLANTA%20REGIONAL%20COMMISSION'&outFields=NAME,GEOID&outSR=4326&f=json"

    gdf_SD = gpd.read_file(url)

    gdf_SD = gdf_SD.merge(df_SD, left_on='NAME', right_on='Super_district')



    # counties next
    df_county = pd.read_csv('county_final2.csv')

    url = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2021_Population/FeatureServer/9/query?where=PlanningRegion%20%3D%20'ATLANTA%20REGIONAL%20COMMISSION'&outFields=GEOID,NAME&outSR=4326&f=json"

    gdf_county = gpd.read_file(url)

    gdf_county = gdf_county.merge(df_county, left_on='NAME', right_on='County')

    return gdf_SD, gdf_county




# define mapping function for super districts first
def superDistrict_mapper():


    gdf = data_loader()[0]

    # do county outline
    county_outline = data_loader()[1]

    color_labels = [
        (254, 217, 118), # light yellow
        (253, 141, 60), # light orange
        (252, 78, 42), # orange
        (227, 26, 28), # red
        (177, 0, 38) # dark red
    ]

    var_dict = {
        'Current Median Home Value':gdf['zestimate_median'],
        '30-Day Change':gdf['change_median']
    }

    gdf['choro_color'] = pd.cut(
            var_dict[variable],
            bins=len(color_labels),
            labels=color_labels,
            include_lowest=True,
            duplicates='drop'
            )

    initial_view_state = pdk.ViewState(
        latitude=33.77376091504563, 
        longitude=-84.37159715066925, 
        zoom=8, 
        max_zoom=12, 
        min_zoom=8,
        pitch=0,
        bearing=0,
        height=550
    )

    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        pickable=True,
        autoHighlight=True,
        highlight_color = [128, 128, 128, 70],
        opacity=0.5,
        stroked=True,
        filled=True,
        get_fill_color='choro_color',
        get_line_color=[128, 128, 128],
        line_width_min_pixels=1
    )

    geojson2 = pdk.Layer(
        "GeoJsonLayer",
        county_outline,
        pickable=False,
        autoHighlight=False,
        opacity=.7,
        stroked=True,
        filled=False,
        get_line_color=[0, 0, 0],
        line_width_min_pixels=3
    )

    r = pdk.Deck(
        layers=[geojson, geojson2],
        initial_view_state=initial_view_state,
        map_provider='mapbox',
        map_style='light',
        # tooltip=tooltip
        )

    return r

def county_mapper():


    gdf = data_loader()[1]

    initial_view_state = pdk.ViewState(
        latitude=33.77376091504563, 
        longitude=-84.37159715066925, 
        zoom=8, 
        max_zoom=12, 
        min_zoom=8,
        pitch=0,
        bearing=0,
        height=550
    )

    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        pickable=True,
        autoHighlight=True,
        highlight_color = [128, 128, 128],
        opacity=0.5,
        stroked=True,
        filled=True,
        get_fill_color=[50,205,50],
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


col1, col2 = st.columns([1,1])
# create dropdown for summary level
geography = col1.radio(
    'Select geography to summarize:',
    ('Super District', 'County'),
    index=0,
    horizontal=True)

variable = col2.radio(
    'Select variable:',
    ('Current Median Home Value', '30-Day Change'),
    index=1,
    horizontal=True)




# show map
if geography == 'Super District':
    st.pydeck_chart(superDistrict_mapper(), use_container_width=True)
else:
    st.pydeck_chart(county_mapper(), use_container_width=True)

st.markdown("***Data provided via the Zestimate API and Zestimate® home valuation from 5/1/23 to 5/4/23.***")
# st.write("Data collected from May 1, 2023 to May 4, 2024.")

image = Image.open('zillow_logo.png')
st.image(image, width=75)








