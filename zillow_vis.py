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
    #MainMenu, footer {visibility: hidden;}
    section.main > div:has(~ footer ) {
        padding-bottom: 5px;}
    div.block-container{
        padding-top:1.5rem;
        padding-left:1.5rem;
        padding-right:1.5rem;
        }
    div.stActionButton{visibility: hidden;}
    div.stRadio > label{
        display: flex;
        justify-content: center;
    }
    div.stRadio > div{
        display: flex;
        justify-content: center;
    }
</style>
""",
    unsafe_allow_html=True,
)



# define color ramp
color_labels = [
        (254, 217, 118), # light yellow
        (253, 141, 60), # light orange
        (252, 78, 42), # orange
        (227, 26, 28), # red
        (177, 0, 38) # dark red
    ]

# define map starting point
latitude = 33.836717766945384
longitude = -84.37286813567411
zoom = 7.2
height = 525

# data loader
@st.cache_data
def data_loader():

    # super districts first
    gdf_SD = gpd.read_file('superDistrict_joined.gpkg')

    # counties next
    gdf_county = gpd.read_file('county_joined.gpkg')

    return gdf_SD, gdf_county

# define mapping function for super districts first
def superDistrict_mapper():

    gdf = data_loader()[0]

    # do county outline
    county_outline = data_loader()[1]

    var_dict = {
        'Current Median Home Value':gdf['zestimate_median'],
        '30-Day Change':gdf['change_median']
    }

    tooltip_label = {
        'Current Median Home Value':'Median Zestimate: ',
        '30-Day Change':'Median 30-Day Zestimate Change: ',
        }
    
    gdf['zestimate_formatted'] = gdf['zestimate_median'].apply(lambda x: "${:,.0f}".format((x)))
    gdf['change_formatted'] = gdf['change_median'].apply(lambda x: "{:.1f}%".format((x)))

    tooltip_value = {
        'Current Median Home Value':gdf['zestimate_formatted'],
        '30-Day Change':gdf['change_formatted'] ,
        }
    
    gdf['tooltip_label'] = tooltip_label[variable]
    gdf['tooltip_value'] = tooltip_value[variable]

    gdf['choro_color'] = pd.cut(
            var_dict[variable],
            bins=len(color_labels),
            labels=color_labels,
            include_lowest=True,
            duplicates='drop'
            )

    initial_view_state = pdk.ViewState(
        latitude=latitude, 
        longitude=longitude, 
        zoom=zoom, 
        max_zoom=12, 
        min_zoom=8,
        pitch=0,
        bearing=0,
        height=height
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

    # define tooltip
    tooltip = {
            "html": "Super District: <b>{NAME}</b><br>{tooltip_label}<b>{tooltip_value}</b>",
            "style": {"background": "rgba(100,100,100,0.9)", "color": "white", "font-family": "Helvetica", "font-size":"15px"},
            }

    geojson2 = pdk.Layer(
        "GeoJsonLayer",
        county_outline,
        pickable=False,
        autoHighlight=False,
        opacity=.7,
        stroked=True,
        filled=False,
        get_line_color=[0, 0, 0],
        line_width_min_pixels=2
    )

    r = pdk.Deck(
        layers=[geojson, geojson2],
        initial_view_state=initial_view_state,
        map_provider='mapbox',
        map_style='light',
        tooltip=tooltip
        )

    return r

# define mapping function for counties next
def county_mapper():

    gdf = data_loader()[1]

    var_dict = {
        'Current Median Home Value':gdf['zestimate_median'],
        '30-Day Change':gdf['change_median']
    }

    tooltip_label = {
        'Current Median Home Value':'Median Zestimate: ',
        '30-Day Change':'Median 30-Day Zestimate Change: ',
        }
    
    gdf['zestimate_formatted'] = gdf['zestimate_median'].apply(lambda x: "${:,.0f}".format((x)))
    gdf['change_formatted'] = gdf['change_median'].apply(lambda x: "{:.1f}%".format((x)))

    tooltip_value = {
        'Current Median Home Value':gdf['zestimate_formatted'],
        '30-Day Change':gdf['change_formatted'] ,
        }
    
    gdf['tooltip_label'] = tooltip_label[variable]
    gdf['tooltip_value'] = tooltip_value[variable]

    gdf['choro_color'] = pd.cut(
            var_dict[variable],
            bins=len(color_labels),
            labels=color_labels,
            include_lowest=True,
            duplicates='drop'
            )

    initial_view_state = pdk.ViewState(
        latitude=latitude, 
        longitude=longitude, 
        zoom=zoom, 
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
        get_line_color=[0, 0, 0],
        line_width_min_pixels=2
    )

    # define tooltip
    tooltip = {
            "html": "County: <b>{NAME}</b><br>{tooltip_label}<b>{tooltip_value}</b>",
            "style": {"background": "rgba(100,100,100,0.9)", "color": "white", "font-family": "Helvetica", "font-size":"15px"},
            }

    r = pdk.Deck(
        layers=geojson,
        initial_view_state=initial_view_state,
        map_provider='mapbox',
        map_style='light',
        tooltip=tooltip
        )

    return r


col1, col2, col3 = st.columns([1,1,1])

# create dropdown for summary level
geography = col2.radio(
    'Select geography to summarize:',
    ('County', 'Super District'),
    index=0,
    horizontal=True
)

variable = '30-Day Change'


# show map
if geography == 'Super District':
    st.pydeck_chart(superDistrict_mapper(), use_container_width=True)
elif geography == 'County':
    st.pydeck_chart(county_mapper(), use_container_width=True)
else:
    st.write("")

st.markdown("***Data provided via the Zestimate API and Zestimate® home valuation from 5/1/23 to 5/4/23.***")
# st.write("Data collected from May 1, 2023 to May 4, 2024.")

image = Image.open('zillow_logo.png')
st.image(image, width=75)








