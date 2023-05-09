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

# color_labels_CT = [
#     (255, 255, 204),
#     (255, 237, 160),
#     (254, 217, 118),
#     (254, 178, 76),
#     (253, 141, 60),
#     (252, 78, 42),
#     (227, 26, 28),
#     (189, 0, 38),
#     (128, 0, 38)
# ]

# define map starting point
latitude = 33.836717766945384
longitude = -84.37286813567411
zoom = 7.2
height = 525

# data loader
@st.cache_data
def data_loader():

    # # census tracts first
    # df_tract = pd.read_csv('CT_final2.csv')

    # df_tract['Census_tract'] = df_tract['Census_tract'].astype(str)

    # url1 = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2021_Population/FeatureServer/21/query?where=PlanningRegion%20%3D%20'ATLANTA%20REGIONAL%20COMMISSION'&outFields=GEOID&outSR=4326&f=json"

    # gdf_tract = gpd.read_file(url1)

    # gdf_CT = gdf_tract.merge(df_tract, left_on='GEOID', right_on='Census_tract')

    # super districts next
    df_SD = pd.read_csv('superDistrict_final2.csv')

    url2 = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2021_Population/FeatureServer/20/query?where=PlanningRegion%20%3D%20'ATLANTA%20REGIONAL%20COMMISSION'&outFields=&outSR=4326&f=json"

    gdf_SD = gpd.read_file(url2)

    gdf_SD = gdf_SD.merge(df_SD, left_on='NAME', right_on='Super_district')

    # counties last
    df_county = pd.read_csv('county_final2.csv')

    url3 = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2021_Population/FeatureServer/9/query?where=PlanningRegion%20%3D%20'ATLANTA%20REGIONAL%20COMMISSION'&outFields=GEOID,NAME&outSR=4326&f=json"

    gdf_county = gpd.read_file(url3)

    gdf_county = gdf_county.merge(df_county, left_on='NAME', right_on='County')

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
        line_width_min_pixels=3
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

# def CT_mapper():

#     gdf = data_loader()[2]

#     # do county outline
#     county_outline = data_loader()[1]

    
#     gdf['zestimate_formatted'] = gdf['zestimate_median'].apply(lambda x: "${:,.0f}".format((x)))
#     gdf['change_formatted'] = gdf['change_median'].apply(lambda x: "{:.1f}%".format((x)))

#     tooltip_value = {
#         'Current Median Home Value':gdf['zestimate_formatted'],
#         '30-Day Change':gdf['change_formatted'] ,
#         }
    

#     gdf['tooltip_value'] = tooltip_value[variable]

#     gdf['choro_color'] = pd.cut(
#             gdf['change_median'],
#             bins=len(color_labels_CT),
#             labels=color_labels_CT,
#             include_lowest=True,
#             duplicates='drop'
#             )

#     initial_view_state = pdk.ViewState(
#         latitude=latitude, 
#         longitude=longitude, 
#         zoom=zoom, 
#         max_zoom=12, 
#         min_zoom=8,
#         pitch=0,
#         bearing=0,
#         height=height
#     )

#     geojson = pdk.Layer(
#         "GeoJsonLayer",
#         gdf,
#         pickable=True,
#         autoHighlight=True,
#         highlight_color = [128, 128, 128, 70],
#         opacity=0.5,
#         stroked=True,
#         filled=True,
#         get_fill_color='choro_color',
#         get_line_color=[128, 128, 128],
#         line_width_min_pixels=1
#     )

#     # define tooltip
#     tooltip = {
#             "html": "Median 30-Day Zestimate Change: <b>{tooltip_value}</b>",
#             "style": {"background": "rgba(100,100,100,0.9)", "color": "white", "font-family": "Helvetica", "font-size":"15px"},
#             }

#     geojson2 = pdk.Layer(
#         "GeoJsonLayer",
#         county_outline,
#         pickable=False,
#         autoHighlight=False,
#         opacity=.7,
#         stroked=True,
#         filled=False,
#         get_line_color=[0, 0, 0],
#         line_width_min_pixels=3
#     )

#     r = pdk.Deck(
#         layers=[geojson, geojson2],
#         initial_view_state=initial_view_state,
#         map_provider='mapbox',
#         map_style='light',
#         tooltip=tooltip
#         )

#     return r

# # # define function for drawing bar chart
# # def superDistrict_charter():

#     gdf = data_loader()[0]

#     df = gdf.drop(['geometry'], axis=1)

#     var_dict = {
#         'Current Median Home Value':'zestimate_median',
#         '30-Day Change':'change_median'
#     }

#     var_dict2 = {
#             'Current Median Home Value':df['zestimate_median'],
#             '30-Day Change':df['change_median']
#         }
    
#     color_labels2 = [
#         'fifth group', 
#         'fourth group', 
#         'third group', 
#         'second group', 
#         'first group'
#     ]

#     df['color_group'] = pd.cut(
#             var_dict2[variable],
#             bins=len(color_labels2),
#             labels=color_labels2,
#             include_lowest=True,
#             duplicates='drop'
#             )
    
#     if geography == 'Super District':
#         df = df.sort_values(by=var_dict[variable], ascending=False).head(20)

#     fig = px.bar(df, 
#                  x=var_dict[variable], 
#                  y="NAME", 
#                  orientation='h',
#                  color='color_group',
#                  hover_name='NAME',
#                  hover_data=['change_median'],
#                 #  custom_data=['NAME', var_dict[variable]],
#                  color_discrete_sequence=["rgb(177, 0, 38)", "rgb(227, 26, 28)", "rgb(252, 78, 42)", "rgb(253, 141, 60)", "rgb(254, 217, 118)"],
#                  title='Top Super Districts',
#                  height=600,
#                  labels={
#                     'change_median':'Median 30-Day Change (%)',
#                     'zestimate_median':'Median Zestimate'
#                  })
       

#     fig.update_layout(
#         margin=dict(l=20, r=20, t=22, b=20),
#         bargap=0.55,
#         yaxis = dict(
#                 autorange='reversed',
#                 title = None,
#                 tickfont_color = '#022B3A',
#                 tickfont_size = 14,
#                 showgrid = False,
#                 ticks='outside',
#                 showline=True,
#                 ),
#         xaxis = dict(
#             ticks='outside',
#             tickformat = ".2",
#             showline=True
#         ),
#         showlegend=False,
#     )

#     return fig



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








