# authors: Jasmine Qin, Keanna Knebel
# date: 2020-06-15

###############################################################################
# IMPORT PACKAGES                                                             #
###############################################################################

# Basics
import pandas as pd
import geopandas as gpd
import numpy as np
import random
import json
import re
from textwrap import dedent

# Plotly
import plotly.graph_objects as go
import plotly.express as px

# Dash
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

# Model
from joblib import load
from shapely.ops import nearest_points
from shapely.geometry import Point
from sklearn import metrics

###############################################################################
# APP SET-UP                                                                  #
###############################################################################

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

###############################################################################
# READ-IN DATASETS                                                            #
###############################################################################

census = pd.read_csv("data/processed/census_viz.csv")
parking_df = gpd.read_file("data/processed/vis_parking.csv")
licence = pd.read_csv("data/processed/vis_licence.csv")
boundary_df = gpd.read_file("data/raw/local_area_boundary.geojson"
                            ).rename(columns={'name': 'LocalArea'})
agg_licence = pd.read_csv("data/processed/vis_agg_licence.csv")

with open("data/raw/local_area_boundary.geojson") as f:
    boundary = json.load(f)

for i in boundary['features']:
    i['name'] = i['properties']['name']
    i['id'] = i['properties']['mapid']

###############################################################################
# MODELLING                                                                   #
###############################################################################

raw_vis_model = pd.read_csv("data/processed/vis_model.csv")
y_valid = raw_vis_model[raw_vis_model.type == 'valid']['label']
y_valid_pred = raw_vis_model[raw_vis_model.type == 'valid']['predict']

# load model
model = load('results/final_model.joblib')

census_cols = list(raw_vis_model.iloc[:, 14:109].columns)
vis_model = raw_vis_model.drop(columns=census_cols)

vis_model['geometry'] = [
    Point(vis_model['coord-y'].iloc[i],
          vis_model[
              'coord-x'].iloc[i]) for i in range(len(vis_model['coord-x']))]
vis_model_gpd = gpd.GeoDataFrame(
    vis_model, crs={'init': 'epsg:4326'}, geometry='geometry')

# define functions


def get_census_info(year, localarea):
    """This function gets the census information for prediction."""
    census_info = raw_vis_model[(raw_vis_model.FOLDERYEAR == year) & (
        raw_vis_model.LocalArea == localarea)][census_cols].iloc[1]
    return census_info.to_dict()


def get_similar_business(p, gpd):
    """This function gets the nearby similar businesses in a dataframe"""
    other_points = gpd["geometry"].unary_union
    nearest_geoms = nearest_points(p, other_points)
    nearest_data = gpd.loc[gpd["geometry"] == nearest_geoms[1]]

    nearest_data['coord-x'] = [i + random.uniform(
        -0.0001, 0.0001) for i in nearest_data['coord-x']]
    nearest_data['coord-y'] = [i + random.uniform(
        -0.0001, 0.0001) for i in nearest_data['coord-y']]

    return nearest_data


# static pie chart
def confusion_matrix():
    matrix = metrics.confusion_matrix(y_true=y_valid, y_pred=y_valid_pred)
    tn, fp, fn, tp = matrix.ravel()

    values = [tp, fn, fp, tn]
    labels_t = ["True Positive",
                "False Negative",
                "False Positive",
                "True Negative"]
    labels = ["TP", "FN", "FP", "TN"]
    colors = ['forestgreen',
              'firebrick',
              'darkorange',
              'powderblue']

    return go.Figure(
        data=go.Pie(
            labels=labels_t,
            values=values,
            hoverinfo='label+value+percent',
            textinfo='text+value',
            text=labels,
            sort=False,
            marker=dict(
                colors=colors,
                line=dict(color='#000000', width=1))
        ),

        layout=go.Layout(
            title='Confusion Matrix',
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
            plot_bgcolor='rgb(0,0,0)',
            legend=dict(
                bgcolor='rgba(255,255,255,0)',
                orientation='h'
            )
        )
    )

###############################################################################
# DATA WRANGLING + REQUIRED INFORMATION                                       #
###############################################################################


# Business licence wrangling
licence = licence[licence.Status == 'Issued']

industries = licence.BusinessIndustry.unique()
localareas = boundary_df.LocalArea.unique()
years = sorted(list(vis_model.FOLDERYEAR.unique()))
businesstypes = agg_licence.BusinessType.unique()

bt_lookup = {}
for i in agg_licence.BusinessIndustry.unique():
    bt_lookup[i] = list(agg_licence.loc[
        agg_licence.BusinessIndustry == i].BusinessType.unique())
bt_lookup['allindustry'] = businesstypes

# wrangle for choropleth (for future implementations)
number_of_businesses = licence.groupby(
    'LocalArea')['BusinessName'].apply(
    lambda x: np.log(len(x.unique())))
boundary_df = boundary_df.merge(pd.DataFrame(
    number_of_businesses).reset_index(), how="left", on='LocalArea')

# Census Dataset Wrangling
edu_df = census[['LocalArea', 'Year',
                 'University',
                 'College',
                 'Apprenticeship/Trades',
                 'High school',
                 'No certificate/diploma']]

occ_df = census[['LocalArea', 'Year',
                 'Management',
                 'Business and finance',
                 'Natural and applied sciences',
                 'Health',
                 'Social Science and education',
                 'Art',
                 'Sales and service',
                 'Trades and transport',
                 'Natural resources and agriculture',
                 'Manufacturing and utilities',
                 'Occupations n/a']]
occ_df = occ_df.rename(columns={'Occupations n/a': 'Other'})

age_df = census[['LocalArea', 'Year',
                 'Under 20',
                 '20 to 34',
                 '35 to 44',
                 '45 to 54',
                 '55 to 64',
                 '65 to 79',
                 '80 and Older']]

size_df = census[['LocalArea',
                  'Year',
                  '1 person',
                  '2 persons',
                  '3 persons',
                  '4 to 5 persons',
                  '6+ persons']]

lang = census[['LocalArea', 'Year', 'English', 'French',
               'Chinese languages', 'Tagalog (Filipino)',
               'Panjabi (Punjabi)', 'Italian', 'German',
               'Spanish', 'Vietnamese', 'Korean language',
               'Hindi', 'Persian (Farsi)']]
lang = lang.rename(columns={'Chinese languages': 'Chinese',
                            'Korean language': 'Korean'})

eth = census[['LocalArea', 'Year', 'Caucasian', 'Arab', 'Black',
              'Chinese', 'Filipino', 'Japanese', 'Korean',
              'Latin American', 'West Asian', 'South Asian',
              'Southeast Asian']]

tenure_df = census[['LocalArea', 'Year',
                    'Owned',
                    'Rented']]

dwel_df = census[['LocalArea',
                  'Year',
                  'Apartment (<5 storeys)',
                  'Apartment (5+ storeys)',
                  'House']]

trans_df = census[['LocalArea',
                   'Year',
                   'car as driver',
                   'car as passenger',
                   'public transportation',
                   'walked',
                   'bicycle',
                   'other transportation']]
trans_df = trans_df.rename(
    columns={'car as driver': 'Car, as Driver',
             'car as passenger': 'Car, as Passenger',
             'public transportation': 'Public Transportation',
             'walked': 'Walk',
             'bicycle': 'Bicycle',
             'other transportation': 'Other'})

park = parking_df[['LocalArea', 'coord-x', 'coord-y']]

list_of_neighbourhoods = {
    'Arbutus-Ridge': {'lat': 49.254093, 'lon': -123.160461},
    'Downtown': {'lat': 49.2807, 'lon': -123.118981},
    'Fairview': {'lat': 49.264, 'lon': -123.13},
    'Grandview-Woodland': {'lat': 49.275, 'lon': -123.067},
    'Hastings-Sunrise': {'lat': 49.2761, 'lon': -123.04426},
    'Marpole': {'lat': 49.211599, 'lon': -123.130448},
    'Riley Park': {'lat': 49.245922, 'lon': -123.103415},
    'Shaughnessy': {'lat': 49.245, 'lon': -123.133},
    'Strathcona': {'lat': 49.273092, 'lon': -123.089429},
    'West End': {'lat': 49.285, 'lon': -123.134},
    'Dunbar-Southlands': {'lat': 49.24798, 'lon': -123.18886},
    'Kerrisdale': {'lat': 49.23376, 'lon': -123.1564},
    'Killarney': {'lat': 49.223, 'lon': -123.039},
    'Kitsilano': {'lat': 49.266031, 'lon': -123.165368},
    'South Cambie': {'lat': 49.246, 'lon': -123.122},
    'Victoria-Fraserview': {'lat': 49.22094, 'lon': -123.06643},
    'Kensington-Cedar Cottage': {'lat': 49.24834, 'lon': -123.07341},
    'Mount Pleasant': {'lat': 49.260, 'lon': -123.108},
    'Oakridge': {'lat': 49.226424, 'lon': -123.123059},
    'Renfrew-Collingwood': {'lat': 49.2425, 'lon': -123.0466},
    'Sunset': {'lat': 49.224, 'lon': -123.089},
    'West Point Grey': {'lat': 49.268244, 'lon': -123.202815},
}

# Main app colour scheme
colors = {
    'ubc': 'rgb(82, 82, 122)',  # UBC logo color 52527a
    'deetken': 'rgb(180, 197, 228)',  # Deetken logo color 7c99d0
    'purple2': 'rgb(240, 240, 245)',
    'green3': 'rgb(117, 163, 129)'
}

# Plotly graph config
config = {'displayModeBar': False, 'scrollZoom': False}


###############################################################################
# HELPER FUNCTIONS                                                            #
###############################################################################


# Descriptive modal overlay for the graphs
def build_info_overlay(id, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div([  # modal div
        html.Div([  # content div
            html.Div([
                html.H3([
                    "Info",
                    html.Img(
                        id=f'close-{id}-modal',
                        src="assets/exit.svg",
                        n_clicks=0,
                        className='info-icon',
                        style={'margin': 0},
                    ),
                ], style={'color': 'white'}),
                dcc.Markdown(
                    content
                ),
            ])
        ],
            className='modal-content',
        ),
        html.Div(className='modal')
    ],
        id=f"{id}-modal",
        style={"display": "none"},
    )

    return div


# Get nearest census year and local area
def get_year_area(year, clickData):
    # select nearest census year
    if year <= 2003:
        census_year = 2001
    elif year <= 2008:
        census_year = 2006
    elif year <= 2013:
        census_year = 2011
    else:
        census_year = 2016

    # select local area
    if clickData is not None:
        area = (clickData['points'][0]['location'])
    else:
        area = 'City of Vancouver'

    return census_year, area


# Filter dataset by area and year, and melt
def get_filter_melt(df, census_year, area):
    df_filtered = df[(df.Year == census_year) & (df.LocalArea == area)]
    df_filtered = df_filtered.melt(id_vars=['LocalArea', 'Year'])
    return df_filtered


# Create Tables for census data visualization
def build_table(df, col_name, area, census_year, clickData):

    # filter by area and year
    df_filtered = df[(df.Year == census_year) & (
        df.LocalArea.isin([area, 'City of Vancouver']))]
    df_filtered.drop(columns=['Year'], inplace=True)
    df_filtered.set_index('LocalArea', inplace=True)
    df_filtered = df_filtered.T

    # select the top 5 values
    df_filtered = df_filtered.sort_values(by=[area], ascending=False)
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered[0:5].copy()

    # format long neighbourhood names
    name_area = re.sub(r"-", "-<br>", area)

    if clickData is not None:
        # format results in table
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[col_name,
                                (name_area.upper() + "<br>(% of population)"),
                                'CITY OF VANCOUVER<br>(% of population)'],
                        fill_color=colors['deetken'],
                        align=['center'],
                        font=dict(color='white', size=22),
                        height=40),
                    cells=dict(
                        values=[df_filtered['index'],
                                round(df_filtered[area]*100, 2),
                                round(df_filtered[
                                    'City of Vancouver']*100, 2)],
                        fill=dict(color=['white']),
                        suffix=['', '%'],
                        align=['center'],
                        font_size=20,
                        height=35)
                )
            ]
        )
    else:
        # format results in table
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[col_name,
                                (area.upper() + "<br>(% of population)")],
                        fill_color=colors['deetken'],
                        align=['center'],
                        font=dict(color='white', size=22),
                        height=40),
                    cells=dict(
                        values=[df_filtered['index'],
                                round(df_filtered[area]*100, 2)],
                        fill=dict(color=['white']),
                        suffix=['', '%'],
                        align=['center'],
                        font_size=20,
                        height=35)
                )
            ]
        )
    fig.update_layout(
        height=300,
        margin={'l': 10, 'r': 10, 't': 10, 'b': 10})

    return fig


# Create bar graph for census data visualization
def build_bar(df, census_year, area, clickData, xaxis, yaxis, range=None):

    area_df = get_filter_melt(df, census_year, area)

    fig = go.Figure(
        data=go.Bar(
            x=area_df['variable'],
            y=area_df['value']*100,
            name=area,
            marker_color='#19B1BA',
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"),
        layout=go.Layout(
            margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
            template='simple_white',
            plot_bgcolor=colors['purple2']))

    if clickData is not None:
        van_df = get_filter_melt(df, census_year, "City of Vancouver")

        fig.add_trace(
            go.Bar(
                x=van_df['variable'],
                y=van_df['value']*100,
                name='City of Vancouver',
                marker_color='#afb0b3',
                hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
            ))

    fig.update_layout(
        barmode='group',
        xaxis_title=xaxis,
        yaxis_title=yaxis,
        showlegend=True,
        legend=dict(x=1, y=1, xanchor="right",
                    bgcolor=colors['purple2']),
        height=350)
    if range:
        fig.update_yaxes(range=range)

    return fig

###############################################################################
# LAYOUT                                                                      #
###############################################################################

########################################
# TAB 1 - Licence visualization layout #
########################################


def build_tab1():
    return html.Div(
        className='row',
        children=[
            html.Div(children=[
                # histogram info
                build_info_overlay("histogram", dedent("""
                The **Industry/Type Distribution** panel displays the total
                count of businesses based in Vancouver in each industry from
                1997 to 2020. When you select a specific industry, it shows the
                distribution of business types grouped under the same industry
                based on North American Industry Classification System (NAICS).
                """)),
                # line info
                build_info_overlay("line", dedent("""
                The **Industry/Type Trend** panel displays the total annual
                number of businesses based in Vancouver from 1997 to 2020
                in all industries. When you select an industry or business
                type, it shows a trend for that specific category.
                """)),
            ]),

            html.Div(
                className="app__content",
                children=[
                    # left-panel user input and local area choropleth
                    html.Div(
                        className="one-third column user__control__panel",
                        children=[
                            # drop-down menus
                            html.Div(
                                className="graph__container first",
                                children=[
                                    html.P(
                                        """Select a business industry
                                        in a Vancouver neighbourhood:"""
                                    ),

                                    html.Div(
                                        className="div-for-dropdown",
                                        children=[
                                            dcc.Dropdown(
                                                id="industry-dropdown",
                                                options=[
                                                    {'label': i, 'value': i}
                                                    for i in industries
                                                ],
                                                style={
                                                    "border": "0px solid black"
                                                },
                                                placeholder='Select a business industry'
                                            )
                                        ],
                                    ),

                                    html.Div(
                                        className="div-for-dropdown",
                                        children=[
                                            dcc.Dropdown(
                                                id="localarea-dropdown",
                                                options=[
                                                    {"label": i, "value": i}
                                                    for i in localareas
                                                ],
                                                style={
                                                    "border": "0px solid black"
                                                },
                                                placeholder='Select a neighbourhood'
                                            )
                                        ]
                                    ),

                                    html.Div(
                                        className="div-for-dropdown",
                                        children=[
                                            dcc.Dropdown(
                                                id="businesstype-dropdown-tab1",
                                                options=[{'label': k,
                                                          'value': k}
                                                         for k in bt_lookup.keys()],
                                                style={
                                                    "border": "0px solid black"
                                                },
                                                placeholder='Select a business type'
                                            )
                                        ]
                                    ),
                                ]
                            ),

                            # choropleth
                            html.Div(
                                className="graph__container second",
                                children=[
                                    dcc.Graph(
                                        id='localarea-map',
                                        config={'displayModeBar': False,
                                                'scrollZoom': False})
                                ]
                            )
                        ]
                    ),

                    # right-panel main map
                    html.Div(
                        className="two-thirds column map__slider__container",
                        children=[
                            # map
                            dcc.Graph(id='scatter-map'),


                            # slider
                            html.Div(
                                className='div-for-slider',
                                children=[
                                    dcc.Slider(
                                        id='year-slider',
                                        min=licence['FOLDERYEAR'].min(),
                                        max=licence['FOLDERYEAR'].max(),
                                        value=2010,
                                        marks={str(year): {
                                            'label': str(year),
                                            'style': {'color': 'white'}}
                                            for year in years},
                                        step=None
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),


            # bottom-panel charts
            html.Div(
                className="app__content",
                children=[

                    # business type histogram
                    html.Div(
                        id="histogram-div",
                        className="one-half column bottom__box",
                        children=[
                            # graph title
                            html.Div(
                                className="graph__title",
                                children=[
                                    html.H4(
                                        id='histogram-title'),

                                    html.Img(
                                        id='show-histogram-modal',
                                        src="assets/question.svg",
                                        n_clicks=0,
                                        className='info-icon'
                                    )
                                ]
                            ),

                            dcc.Graph(id="business-type-histogram",
                                      config={'displayModeBar': False}),
                        ]
                    ),

                    # line chart
                    html.Div(
                        id="line-div",
                        className="other-half column bottom__box",
                        children=[
                            # graph title
                            html.Div(
                                className="graph__title",
                                children=[
                                    html.H4(
                                        id='line-title'),

                                    html.Img(
                                        id='show-line-modal',
                                        src="assets/question.svg",
                                        n_clicks=0,
                                        className='info-icon'
                                    )
                                ]
                            ),

                            dcc.Graph(id="business-industry-line",
                                      config={'displayModeBar': False})
                        ],
                    ),
                ],
            ),
        ])


########################################
# TAB 2 - Census visualization layout  #
########################################


def build_tab2():
    return html.Div(
        children=[
            html.Div(
                className="app__content",
                children=[
                    html.Div(
                        className="one-fifth column offset-by-four-fifths",
                        children=[
                            # clear selection button
                            html.Button(
                                id='clearButton',
                                n_clicks=0,
                                children='Clear Neighbourhood Selection'),
                        ],
                    )
                ], style={'marginTop': 10, 'marginBottom': 5}
            ),

            # main row with map and summary info
            html.Div(
                className='row',
                children=[
                    html.Div(
                        className="app__content",
                        children=[
                            # summary info
                            html.Div(
                                id="summary_info",
                                className="one-third column user__control__panel",
                            ),
                            # main map of neighbourhoods
                            html.Div(
                                className="two-thirds column map__slider__container",
                                children=[
                                    # map
                                    dcc.Graph(
                                        id='van_map',
                                        style={
                                            "visibility": "visible"},
                                        config=config),

                                    # slider
                                    html.Div(
                                        className='div-for-slider',
                                        children=[
                                            dcc.Slider(
                                                id='year_slider_census',
                                                min=licence['FOLDERYEAR'].min(
                                                ),
                                                max=licence['FOLDERYEAR'].max(
                                                ),
                                                value=2016,
                                                marks={str(year): {
                                                    'label': str(year),
                                                    'style': {'color': 'white'}
                                                    }
                                                    for year in licence['FOLDERYEAR'].unique()},
                                                step=None
                                            )
                                        ]
                                    )
                                ]
                            )
                        ], style={'marginTop': 0}
                    )
                ], style={'marginTop': 0}

            ),

            # Adding tabs for summary neighbourhood data
            dcc.Tabs(id="subTabs", children=[

                # summary of local demographics
                dcc.Tab(label='PEOPLE', children=[
                        html.Div(
                            id="people-info-overlay",
                            children=[
                                # age graph info
                                build_info_overlay('age', ""),
                                # household size graph info
                                build_info_overlay('size', ""),
                                # language table info
                                build_info_overlay('lang', ""),
                                # ethnicity table info
                                build_info_overlay('eth', ""),
                                # education graph info
                                build_info_overlay('edu', ""),
                                # occupation industry info
                                build_info_overlay('occ', ""),
                            ]
                        ),

                        html.Div(
                            className="app__content",
                            children=[
                                # population by age
                                html.Div(
                                    className="one-half2 column bottom__box2",
                                    id="age-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="age-title"),
                                                html.Img(
                                                    id='show-age-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon',
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='age_graph',
                                                  config=config)
                                    ]
                                ),

                                # population by household size
                                html.Div(
                                    className="other-half2 column bottom__box2",
                                    id="size-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="size-title"),
                                                html.Img(
                                                    id='show-size-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='size_graph',
                                                  config=config)
                                    ]
                                )
                            ], style={'marginTop': 50}),

                        # population by language + ethnicity
                        html.Div(
                            className="app__content",
                            children=[
                                html.Div(
                                    className="one-half2 column bottom__box2",
                                    id="lang-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="lang-title"),
                                                html.Img(
                                                    id='show-lang-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='lang_graph',
                                                  config=config)
                                    ]
                                ),
                                html.Div(
                                    className="other-half2 column bottom__box2",
                                    id="eth-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="eth-title"),
                                                html.Img(
                                                    id='show-eth-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='eth_graph',
                                                  config=config)]
                                )
                            ], style={'marginTop': 10}
                        ),

                        # population by education level
                        html.Div(
                            className="app__content",
                            children=[
                                html.Div(
                                    className="one-half2 column bottom__box2",
                                    id="edu-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="edu-title"),
                                                html.Img(
                                                    id='show-edu-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='edu_graph',
                                                  config=config)
                                    ]),
                                html.Div(
                                    className="other-half2 column bottom__box2",
                                    id="occ-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="occ-title"),
                                                html.Img(
                                                    id='show-occ-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='occ_graph',
                                                  config=config)]
                                )
                            ],
                        ),
                        ]),

                # summary of local infrastructure
                dcc.Tab(label='INFRASTRUCTURE', children=[
                        html.Div(
                            id="inf-info-overlay",
                            children=[
                                # housing tenure pie chart info
                                build_info_overlay('tenure', ""),
                                # Dwelling type graph info
                                build_info_overlay('dwelling', ""),
                                # Transportation graph info
                                build_info_overlay('transport', ""),
                                # parking meters map info
                                build_info_overlay('parking', ""),
                            ]
                        ),

                        html.Div(
                            className="app__content",
                            children=[
                                # housing tenure (own vs. rent)
                                html.Div(
                                    className="one-half2 column bottom__box2",
                                    id="tenure-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="tenure-title"),
                                                html.Img(
                                                    id='show-tenure-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='tenure_graph',
                                                  config=config)
                                    ], ),
                                # distribution of dwelling types
                                html.Div(
                                    className="other-half2 column bottom__box2",
                                    id="dwelling-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="dwelling-title"),
                                                html.Img(
                                                    id='show-dwelling-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='dwelling_graph',
                                                  config=config)
                                    ])
                            ], style={'marginTop': 50}),

                        html.Div(
                            className="app__content",
                            children=[
                                # transportation mode
                                html.Div(
                                    className="one-half2 column bottom__box2",
                                    id="transport-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="transport-title"),
                                                html.Img(
                                                    id='show-transport-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='transport_graph',
                                                  config=config)
                                    ], ),
                                # distribution/count of street parking
                                html.Div(
                                    className="other-half2 column bottom__box2",
                                    id="parking-div",
                                    children=[
                                        html.H4(
                                            className="graph__title",
                                            children=[
                                                html.H4(
                                                    id="parking-title"),
                                                html.Img(
                                                    id='show-parking-modal',
                                                    src="assets/question.svg",
                                                    n_clicks=0,
                                                    className='info-icon'
                                                ),
                                            ],
                                        ),
                                        dcc.Graph(id='parking_graph',
                                                  config=config)
                                    ]
                                )
                            ], style={'marginTop': 50}),
                        ]),
            ], style={'marginTop': 50}),
        ])

########################################
# TAB 3 - Modelling Result layout      #
########################################


def build_tab3_user_control():
    return [
        html.Div(
            className="div-for-dropdown3",
            children=[
                dcc.Dropdown(
                    id="localarea-dropdown3",
                    options=[
                        {'label': i, 'value': i}
                        for i in localareas
                    ],
                    placeholder="Neighbourhood: Downtown"
                )
            ],
        ),

        # Business Type
        html.Div(
            className="div-for-dropdown3",
            children=[
                dcc.Dropdown(
                    id="businesstype-dropdown3",
                    options=[
                        {'label': i, 'value': i}
                        for i in businesstypes
                    ],
                    placeholder="Business type: Retail Dealer"
                )
            ],
        ),

        # History
        html.Div(
            className="div-for-dropdown3",
            children=[
                dcc.Dropdown(
                    id="history-dropdown3",
                    options=[
                        {'label': 'greater than 5 years',
                         'value': 1},
                        {'label': 'less than 5 years',
                         'value': 0}
                    ],
                    placeholder='History: greater than 5 years'
                )
            ],
        ),

        html.Hr(),

        # Business Name
        html.Div(
            className="div-for-input",
            children=[
                dcc.Input(
                    id="businessname-input3",
                    type="text",
                    placeholder="Business Name"
                ),
            ],
        ),

        # Latitude
        html.Div(
            className="div-for-input",
            children=[
                dcc.Input(
                    id="lat-input3",
                    type="number",
                    placeholder="Latitude: 49.2822434350563"
                )
            ],
        ),

        # Longitude
        html.Div(
            className="div-for-input",
            children=[
                dcc.Input(
                    id="lon-input3",
                    type="number",
                    placeholder="Longitude: -123.119500778402"
                )
            ],
        ),

        # Fee paid
        html.Div(
            className="div-for-input",
            children=[
                dcc.Input(
                    id="fee-input3",
                    type="number",
                    placeholder="Fee paid (CAD): 50"
                )
            ],
        ),

        # Number of employees
        html.Div(
            className="div-for-input",
            children=[
                dcc.Input(
                    id="employee-input3",
                    type="number",
                    placeholder="Number of employees: 5"
                )
            ],
        ),

        html.Hr(),

        html.P(id="predict_text1"),

        html.P(id="predict_text2"),
    ]


def build_tab3():
    return html.Div(
        className="app__content",
        children=[
            html.Div(children=[
                # model map info
                build_info_overlay("model", dedent("""
                This map is designed to visualize the model's
                performance metric - **Recall Score**. \n
                When the predicted result is ***"will renew"***, all renewed
                businesses of the same type in the selected year are plotted
                on the map. Red points represent *false negatives*, whereas
                blue points represent *true positives*. \n
                When the predicted result is ***"will not renew"***, all
                non-renewed businesses of the same type in the selected year
                are plotted on the map.
                Red points represent *false positives*, whereas blue points
                represent *true negatives*. \n
                The colour represents the model's level of confidence.
                The darker the colour, the higher the predicted probability.
                Only magnitudes matter here and negative signs are
                assigned for colouring.
                """)),
            ]),

            html.Div(
                className="one-fourth column user__control__panel",
                children=[
                    html.Div(
                        className="graph__container third",
                        children=[

                            dcc.Tabs(
                                id="tab3-tabs",
                                children=[

                                    # Info tab
                                    dcc.Tab(
                                        label="Info",
                                        id="info-tab",
                                        children=[
                                            html.H6(
                                                className="tab3-info-titles",
                                                children="What's on this tab?"),
                                            html.P(
                                                className="tab3-info-texts",
                                                children="""
                                                This tab allows
                                                you to input specific information about
                                                a business. The machine learning model will
                                                generate a renewal probability
                                                and model performances will be plotted
                                                on the map.
                                                """),
                                            html.Hr(),
                                            html.H6(
                                                className="tab3-info-titles",
                                                children="How to use this tab?"),
                                            html.P(
                                                className="tab3-info-texts",
                                                children="""
                                                You can navigate to the "Inputs" tab
                                                and fill in neighbourhood, business type, history,
                                                fee paid, and number of employees. If coordinates
                                                are provided, nearby similar businesses will appear
                                                on the map.
                                                """),
                                        ]
                                    ),

                                    # Model Input tab
                                    dcc.Tab(
                                        label="Inputs",
                                        id="model-inputs-tab",
                                        children=build_tab3_user_control()
                                    )
                                ]
                            ),
                        ]
                    )
                ]
            ),

            html.Div(
                className="two-fourths column map__slider__container3",
                id="model-div",
                children=[
                    # model map
                    dcc.Graph(id='model-map'),

                    # year slider
                    html.Div(
                        className='div-for-slider3',
                        children=[
                            dcc.Slider(
                                id='year-slider3',
                                min=licence['FOLDERYEAR'].min(),
                                max=licence['FOLDERYEAR'].max(),
                                value=2019,
                                marks={str(year): {
                                    'label': str(year),
                                    'style': {'color': 'white'}}
                                    for year in years},
                                step=None
                            ),

                            html.Img(
                                id='show-model-modal',
                                src="assets/question.svg",
                                n_clicks=0,
                                className='info-icon'
                            ),
                        ],
                    ),
                ],
            ),

            # Confusion matrix
            html.Div(
                className="one-fourth column user__control__panel",
                children=[
                    html.Div(
                        className="graph__container third",
                        children=[
                            dcc.Graph(
                                id='confusion-matrix',
                                figure=confusion_matrix(),
                                config=config
                            ),

                            html.P(className="tab3-info-texts",
                                   children="""
                                   Current model: Light-GBM
                                   """)

                        ]
                    )
                ],
            )
        ],
    )


########################################
# MAIN APP LAYOUT                      #
########################################
app.layout = html.Div([

    # Main app header
    html.Div([
        # Setting the main title of the Dashboard
        html.H1(
            "Understanding the Evolution of Vancouver's Business Landscape",
            style={"textAlign": "center", 'fontFamily': 'Open Sans',
                   'marginTop': 40, 'marginBottom': 40,
                   'marginLeft': 100, 'marginRight': 100,
                   'color': "black"})],),

    # Dividing the dashboard into tabs
    dcc.Tabs(id="mainTabs", children=[

        # Define the layout of the first Tab
        dcc.Tab(label='BUSINESS LICENCE',
                id='tab1',
                className='custom-tab',
                children=[
                    build_tab1()
                ]),

        # Define the layout of the second Tab
        dcc.Tab(label='NEIGHBOURHOOD PROFILES',
                id='tab2',
                className='custom-tab',
                children=[
                    build_tab2()
                ]),

        # Define the layout of the third Tab
        dcc.Tab(label='MACHINE LEARNING MODEL',
                id='tab3',
                className='custom-tab',
                children=[
                    build_tab3()
                ])
    ]),

    # main app footer
    html.Footer(id="footer", children=[

        html.H1("Project Partners",
                style={"textAlign": "center", 'fontFamily': 'Open Sans',
                       'marginBottom': 10, 'marginTop': 10,
                       'color': "black"}),

        dbc.Row(children=[

            html.Img(
                id="ubc-logo",
                src="https://brand3.sites.olt.ubc.ca/files/2018/09/5NarrowLogo_ex_768.png",
                style={"width": "20%"}),

            html.Img(
                id="deetken-logo",
                src="https://deetken.com/wp-content/uploads/2019/02/logo-1.png",
                style={"width": "20%"}),

        ]),

    ], style={'marginTop': 50}),
])

###############################################################################
# UPDATES + CALLBACKS                                                         #
###############################################################################

########################################
# TAB 1 - UPDATES                      #
########################################

# update titles


@app.callback(
    Output("histogram-title", "children"),
    [Input("industry-dropdown", "value")],
)
def update_title_bar(SelectedIndustry):
    if SelectedIndustry:
        return "Total Number of Issued Businesses in by Business Type (1997 to 2020)"
    else:
        return "Total Number of Issued Businesses in all Industries (1997 to 2020)"


@app.callback(
    Output("line-title", "children"),
    [Input("industry-dropdown", "value")],
)
def update_title_line(SelectedIndustry):
    if SelectedIndustry:
        return "Total Number of Issued Businesses by Year"
    else:
        return "Total Number of Issued Businesses in all Industries by Year"


@app.callback(
    Output('businesstype-dropdown-tab1', 'options'),
    [Input('industry-dropdown', 'value')])
def set_bt_options(SelectedIndustry):
    if SelectedIndustry:
        return [{'label': i, 'value': i} for i in bt_lookup[SelectedIndustry]]
    else:
        return [{'label': i, 'value': i} for i in bt_lookup['allindustry']]


# update choropleth
@app.callback(
    Output("localarea-map", "figure"),
    [Input("localarea-dropdown", "value")],
)
def update_choropleth(SelectedLocalArea):

    if SelectedLocalArea:
        boundary_df['color'] = ['not-selected']*22
    else:
        boundary_df['color'] = ['blank']*22

    boundary_df.loc[
        boundary_df.LocalArea == SelectedLocalArea,
        'color'] = 'selected'

    return go.Figure(px.choropleth(
        boundary_df,
        geojson=boundary,
        color="color",
        color_discrete_map={'not-selected': 'white',
                            'selected': colors['ubc'],
                            'blank': colors['deetken']},
        featureidkey="properties.mapid",
        locations="mapid",
        projection="mercator",
        hover_name="LocalArea",
        hover_data={"color": False,
                    "mapid": False}
    )
    ).update_geos(
        fitbounds="locations",
        visible=False
    ).update_layout(
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        coloraxis_showscale=False,
        showlegend=False)


# update histogram
@app.callback(
    Output("business-type-histogram", "figure"),
    [Input("industry-dropdown", "value"),
     Input("localarea-dropdown", "value")],
)
def update_histogram(SelectedIndustry, SelectedLocalArea):
    sum_col = 'BusinessType'

    if SelectedIndustry and SelectedLocalArea:
        histogram_df = agg_licence[
            agg_licence.BusinessIndustry == SelectedIndustry
        ]
        histogram_df = histogram_df[
            histogram_df.LocalArea == SelectedLocalArea
        ]
    elif SelectedIndustry:
        histogram_df = agg_licence[
            agg_licence.BusinessIndustry == SelectedIndustry
        ]
    elif SelectedLocalArea:
        sum_col = 'BusinessIndustry'
        histogram_df = agg_licence[
            agg_licence.LocalArea == SelectedLocalArea
        ]
    else:
        histogram_df = agg_licence.copy()
        sum_col = 'BusinessIndustry'

    histogram_df = pd.DataFrame(
        histogram_df.groupby([sum_col])[
            'business_id'].sum()).reset_index()
    histogram_df = histogram_df.sort_values(
        'business_id')

    histogram_df = histogram_df.rename(
        columns={sum_col: 'y-axis',
                 'business_id': 'x-axis'})

    x_title = "Count of Unique Businesses on Log10 Scale"

    return go.Figure(
        data=go.Bar(x=histogram_df['x-axis'],
                    y=histogram_df['y-axis'],
                    orientation='h',
                    marker_color=colors['green3'],
                    hoverinfo='x'
                    ),
        layout=go.Layout(
            margin={'l': 10, 'r': 10, 't': 20, 'b': 10},
            annotations=[
                dict(
                    x=np.log10(xi),
                    y=yi,
                    text=yi,
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(color=colors['ubc']),
                )
                for xi, yi in zip(histogram_df['x-axis'],
                                  histogram_df['y-axis'])
            ],
            xaxis=go.XAxis(
                title=x_title,
                type="log"),
            yaxis=go.XAxis(
                showticklabels=False),
            plot_bgcolor=colors['purple2'],
        )
    )


# update line
@app.callback(
    Output("business-industry-line", "figure"),
    [Input("industry-dropdown", "value"),
     Input("localarea-dropdown", "value"),
     Input('businesstype-dropdown-tab1', 'value')],
)
def update_line(SelectedIndustry,
                SelectedLocalArea,
                SelectedBusinessType):

    if SelectedIndustry or SelectedLocalArea or SelectedBusinessType:
        line_df = agg_licence.copy()

        if SelectedIndustry:
            line_df = line_df[
                line_df.BusinessIndustry == SelectedIndustry]
        if SelectedLocalArea:
            line_df = line_df[line_df.LocalArea == SelectedLocalArea]
        if SelectedBusinessType:
            line_df = line_df[
                line_df.BusinessType == SelectedBusinessType]

        line_df = pd.DataFrame(line_df.groupby([
            'FOLDERYEAR'])['business_id'].sum()).reset_index()

    else:
        line_df = pd.DataFrame(agg_licence.groupby([
            'FOLDERYEAR'])['business_id'].sum()).reset_index()\

    y_title = "Count of Unique Businesses"

    return go.Figure(
        data=go.Scatter(x=line_df['FOLDERYEAR'],
                        y=line_df['business_id'],
                        mode='lines+markers',
                        marker_color=colors['green3']),

        layout=go.Layout(
            margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
            xaxis=go.XAxis(
                title="Issue Year",
                tickmode='linear',
                tickangle=-45
            ),
            yaxis=go.XAxis(
                title=y_title
            ),
            plot_bgcolor=colors['purple2']
        )
    )


# update map
@app.callback(
    Output('scatter-map', 'figure'),
    [Input('industry-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('localarea-dropdown', 'value'),
     Input('businesstype-dropdown-tab1', 'value')])
def update_figure(SelectedIndustry,
                  SelectedYear,
                  SelectedLocalArea,
                  SelectedBusinessType):
    latInitial = 49.250
    lonInitial = -123.121
    zoom = 11
    opacity = 0.5

    filtered_df = licence[
        licence.FOLDERYEAR == SelectedYear]

    # filter licence data for an industry
    if SelectedIndustry:
        filtered_df = filtered_df[
            filtered_df.BusinessIndustry == SelectedIndustry]
        opacity = 0.7

    # filter licence data for business type
    if SelectedBusinessType:
        filtered_df = filtered_df[
            filtered_df.BusinessType == SelectedBusinessType]
        opacity = 0.8

    # zoom in for selected neighbourhood
    if SelectedLocalArea:
        zoom = 13
        filtered_df = filtered_df[
            filtered_df.LocalArea == SelectedLocalArea]
        latInitial = list_of_neighbourhoods[
            SelectedLocalArea]['lat']
        lonInitial = list_of_neighbourhoods[
            SelectedLocalArea]['lon']
        opacity = 1

    # add colour based on NextYearStatus
    list_of_status = ['Issued', 'Inactive', 'Pending',
                      'Cancelled', 'Gone Out of Business']
    traces = []
    for i in list_of_status:
        df_by_status = filtered_df[
            filtered_df['NextYearStatus'] == i]

        customdata = pd.DataFrame({
            'Business Name': df_by_status.BusinessName,
            'Business Type': df_by_status.BusinessType,
        }
        )

        # choose a status to show on map
        if i == 'Issued':
            traces.append(
                go.Scattermapbox(
                    lat=df_by_status['coord-y'],
                    lon=df_by_status['coord-x'],
                    customdata=customdata,
                    mode="markers",
                    name=i,
                    marker=dict(
                        opacity=opacity,
                        size=4),
                    hovertemplate="Business Name: %{customdata[0]}</b><br>Business Type: %{customdata[1]}"
                )
            )
        else:
            traces.append(
                go.Scattermapbox(
                    lat=df_by_status['coord-y'],
                    lon=df_by_status['coord-x'],
                    customdata=customdata,
                    mode="markers",
                    name=i,
                    marker=dict(
                        opacity=opacity,
                        size=4),
                    visible='legendonly',
                    hovertemplate="Business Name: %{customdata[0]}</b><br>Business Type: %{customdata[1]}"
                )
            )

    return go.Figure(

        data=traces,

        layout=go.Layout(
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
            legend=dict(
                x=0,
                y=1,
                bordercolor="Black",
                borderwidth=0,
                bgcolor="rgb(82, 82, 122)",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="white"
                ),
                orientation="h"
            ),
            font={"color": "#ffffff"},
            mapbox=dict(
                center=dict(
                    lat=latInitial,
                    lon=lonInitial),
                style="carto-positron",
                zoom=zoom,
                bearing=0
            ),
        )
    )


for id in ['histogram', 'line']:
    @app.callback([Output(f"{id}-modal", 'style'),
                   Output(f"{id}-div", 'style')],
                  [Input(f'show-{id}-modal', 'n_clicks'),
                   Input(f'close-{id}-modal', 'n_clicks')])
    def toggle_modal_1(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('show-'):
            return {"display": "block"}, {'zIndex': 1003}
        else:
            return {"display": "none"}, {'zIndex': 0}

########################################
# TAB 2 - UPDATES                      #
########################################


# Define callback to update vancouver map
@app.callback(
    Output('van_map', 'figure'),
    [Input('van_map', 'clickData')])
def update_van_map(clickData):

    boundary_df['color'] = ['blank']*22

    if clickData is not None:
        boundary_df['color'] = ['not-selected']*22
        neighbour = (clickData['points'][0]['location'])
        boundary_df.loc[
            boundary_df.LocalArea == neighbour,
            'color'] = 'selected'

    graph_map = px.choropleth_mapbox(boundary_df,
                                     geojson=boundary,
                                     locations='LocalArea',
                                     featureidkey='properties.name',
                                     opacity=0.5,
                                     color="color",
                                     color_discrete_map={
                                         'not-selected': 'white',
                                         'selected': colors['ubc'],
                                         'blank': colors['deetken']},
                                     hover_name='LocalArea',
                                     hover_data={'LocalArea': False,
                                                 'color': False},
                                     mapbox_style="carto-positron",
                                     center={"lat": 49.252, "lon": -123.140},
                                     zoom=10.9)

    graph_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_showscale=False,
        showlegend=False,
        hoverlabel=dict(
            font_size=16,
            font_family="sans-serif"),
        annotations=[go.layout.Annotation(
            x=0,
            y=1,
            text="Click the map to explore Vancouver Neighbourhoods",
            showarrow=False,
            font=dict(
                family="sans-serif",
                size=20,
                color="White"),
            bordercolor="Black",
            borderwidth=0,
            borderpad=6,
            bgcolor="rgb(71, 71, 107)",
            opacity=0.7)])

    return graph_map


# update graph info overlay by local area + year
@app.callback(
    [Output("people-info-overlay", 'children'),
     Output("inf-info-overlay", "children")],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_people_overlay(clickData, year):

    census_year, area = get_year_area(year, clickData)

    if census_year != 2011:
        data_source = dedent(f"""
            The data source for this graph is the [**{census_year} Canadian
            Census**](https://opendata.vancouver.ca/explore/dataset/census-local-area-profiles-{census_year}/information/),
            hosted on the City of Vancouver’s [Open Data
            Portal](https://opendata.vancouver.ca/pages/home/).
            """)
    else:
        data_source = dedent(f"""
            The data source for this graph is the [**{census_year} Canadian
            Census**](https://opendata.vancouver.ca/explore/dataset/census-local-area-profiles-{census_year}/information/)
            and the [**2011 National Household Survey (NHS)**
            ](https://www12.statcan.gc.ca/nhs-enm/2011/dp-pd/prof/index.cfm?Lang=E).
            These datasets are hosted on the City of Vancouver’s [Open Data
            Portal](https://opendata.vancouver.ca/pages/home/) and the
            [Statistics Canada](https://www.statcan.gc.ca/eng/start) website,
            respectively.
            """)

    deselect_info = dedent(f"""
        If you would like to view just the information for {area}, you can
        deselect the "City of Vancouver" by clicking on its legend entry.""")

    reset_info = dedent("""
        To reset the map and deselect the neighbourhood,
        click on the ***Clear Neighbourhood Selection*** button
        located in the top right hand corner of the page.
        """)

    base_line = dedent("""
    To provide a baseline comparison, the distribution for the City of
    Vancouver is also displayed (grey).
    """)

    van_def = dedent("""
    Here, the City of Vancouver is defined as the total
    area of the combined 22 local neighbourhoods.
    """)

    if clickData is not None:
        people_info = [
            # age graph info
            build_info_overlay('age', ((dedent(f"""
            This graph shows the **Age Distribution** of the population in
            **{area}** (blue line).""") + base_line + deselect_info
                                        + reset_info + data_source))),
            # household size graph info
            build_info_overlay('size', ((dedent(f"""
            This graph shows the distribution of **Household Size** for the
            population in **{area}** (blue); where 'Household size' refers
            to the number of persons
            in a private household.""") + base_line + deselect_info
                                        + reset_info + data_source))),
            # language table info
            build_info_overlay('lang', ((dedent(f"""
            This table shows the top five **Mother Tongue
            Languages** spoken by residents in **{area}**. Here 'Mother tongue'
            refers to the first language learned at home in childhood and still
            understood by the person at the time the data was
            collected.""") + base_line + reset_info + data_source))),
            # ethnicity table info
            build_info_overlay('eth', ((dedent(f"""
            This table shows the top five **Ethnic Origins** of the population
            in **{area}**.""") + base_line + reset_info + data_source))),
            # education graph info
            build_info_overlay('edu', ((dedent(f"""
            This graph shows the distribution of the **Highest Level
            of Education Received** for persons aged 15 years and
            over in **{area}** (blue).""") + base_line + deselect_info
                                           + reset_info + data_source))),
            # occupation industry info
            build_info_overlay('occ', ((dedent(f"""
            This graph shows the distribution of the **Occupation
            Industries** for all employed
            persons in **{area}** (blue).""") + base_line + deselect_info
                                              + reset_info + data_source))),
        ]

        infra_info = [
            # housing tenure pie chart info
            build_info_overlay('tenure', ((dedent(f"""
            This graph shows the proportion of the population in **{area}** who
            **own** their dwelling vs. those who **rent** their dwelling.
            """) + reset_info + data_source))),
            # Dwelling type graph info
            build_info_overlay('dwelling', ((dedent(f"""
            This graph shows the distribution of **Dwelling
            Types** in **{area}** (blue).""") + base_line + deselect_info
                                              + reset_info + data_source))),
            # Transportation graph info
            build_info_overlay('transport', ((dedent(f"""
            This graph shows the distribution of the **Dominant Mode of
            Transportation** for all
            residents in **{area}** (blue).""") + base_line + deselect_info
                                                + reset_info + data_source))),
            # parking meters map info
            build_info_overlay('parking', ((dedent(f"""
            This graph shows the locations and count of the **Metered
            Street Parking Spaces** present in **{area}**.
            """) + reset_info + dedent("""
            The data source for this graph is the [**2019 Parking Meter
            Dataset**](https://opendata.vancouver.ca/explore/dataset/parking-meters/information/),
            hosted on the City of Vancouver’s [Open Data
            Portal](https://opendata.vancouver.ca/pages/home/).
            """)))),
        ]

    else:
        people_info = [
            # age graph info
            build_info_overlay('age', ((dedent(f"""
            This graph shows the **Age Distribution** for the population of
            the **{area}**.""") + van_def + data_source))),
            # household size graph info
            build_info_overlay('size', ((dedent(f"""
            This graph shows the distribution of **Household Size** for the
            population of the **{area}**; where 'Household size' refers
            to the number of persons in a private
            household.""") + van_def + data_source))),
            # language table info
            build_info_overlay('lang', ((dedent(f"""
            This table shows the top five **Mother Tongue
            Languages** spoken by residents in the **{area}**. Here
            'Mother tongue' refers to the first language learned at
            home in childhood and still understood by the person at
            the time the data was collected.
            """) + data_source))),
            # ethnicity table info
            build_info_overlay('eth', ((dedent(f"""
            This table shows the top five **Ethnic Origins** of the
            population in the **{area}**.""") + van_def + data_source))),
            # education graph info
            build_info_overlay('edu', ((dedent(f"""
            This graph shows the distribution of the **Highest Level
            of Education Received** for persons aged 15 years and
            over in the **{area}**.""") + van_def + data_source))),
            # occupation industry info
            build_info_overlay('occ', ((dedent(f"""
            This graph shows the distribution of the **Occupation
            Industries** for all employed persons in
            the **{area}**.""") + van_def + data_source))),
        ]

        infra_info = [
            # housing tenure pie chart info
            build_info_overlay('tenure', ((dedent(f"""
            This graph shows the proportion of the population in the **{area}**
            who **own** their dwelling vs. those who **rent**
            their dwelling.""") + van_def + data_source))),
            # Dwelling type graph info
            build_info_overlay('dwelling', ((dedent(f"""
            This graph shows the distribution of **Dwelling Types** in
            the **{area}**.""") + van_def + data_source))),
            # Transportation graph info
            build_info_overlay('transport', ((dedent(f"""
            This graph shows the distribution of the **Dominant Mode of
            Transportation** for all residents in
            the **{area}**.""") + van_def + data_source))),
            # parking meters map info
            build_info_overlay('parking', ((dedent(f"""
            This graph shows the locations and count of the **Metered
            Street Parking Spaces** present in the **{area}**.
            """) + dedent("""
            The data source for this graph is the [**2019 Parking Meter
            Dataset**](https://opendata.vancouver.ca/explore/dataset/parking-meters/information/),
            hosted on the City of Vancouver’s [Open Data
            Portal](https://opendata.vancouver.ca/pages/home/).
            """)))),
        ]

    return people_info, infra_info


# update education graph by local area
@app.callback(
    [Output("edu-title", 'children'),
     Output("edu_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_edu(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = ("Highest Level of Education Achieved, in " + str(census_year))

    # create bar graph
    fig = build_bar(edu_df,
                    census_year,
                    area,
                    clickData,
                    "Level of Education",
                    "Percent of Total Population")

    return title, fig


# update occupation graph by local area and year
@app.callback(
    [Output("occ-title", 'children'),
     Output("occ_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_occ(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = (
        str(area) + "'s Distribution of Occupation Industries, in " + str(census_year))

    df = get_filter_melt(occ_df, census_year, area)
    df = df.sort_values('value', ascending=False)

    fig = go.Figure(
        data=go.Bar(
            y=df["variable"],
            x=df['value']*100,
            orientation='h',
            name=area,
            marker_color='#19B1BA',
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>"),
        layout=go.Layout(
            margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
            template='simple_white',
            plot_bgcolor=colors['purple2']))

    fig.update_layout(
        barmode='group',
        xaxis={'title': "Percent of Employed Population"},
        showlegend=True,
        legend=dict(x=1, y=1, xanchor="right", bgcolor=colors['purple2']),
        height=350,
        yaxis=go.XAxis(
            showticklabels=False),
        annotations=[
            dict(
                x=xi*100,
                y=yi,
                text=yi,
                xanchor="left",
                yanchor="middle",
                showarrow=False,
                font=dict(color=colors['ubc']),
            )
            for xi, yi in zip(df['value'],
                              df['variable'])
        ],)

    return title, fig


# update age graph by local area
@app.callback(
    [Output("age-title", 'children'),
     Output("age_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_age(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = ("Age Distribution of Population, in " + str(census_year))

    df = get_filter_melt(age_df, census_year, area)

    fig = go.Figure(
        data=go.Scatter(
            x=df['variable'],
            y=df['value']*100,
            mode='lines+markers',
            marker=dict(
                color='#19B1BA',
                size=8),
            name=area,
            line=dict(width=4),
            line_shape='spline',
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"),

        layout=go.Layout(
            margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
            template='simple_white',
            plot_bgcolor=colors['purple2']))

    if clickData is not None:
        van_df = df = get_filter_melt(age_df, census_year, "City of Vancouver")

        fig.add_trace(
            go.Scatter(
                x=van_df['variable'],
                y=van_df['value']*100,
                mode='lines+markers',
                marker=dict(
                    color='#afb0b3',
                    size=8),
                name='City of Vancouver',
                line=dict(width=3),
                line_shape='spline',
                hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))

    fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Percent of Total Population",
        showlegend=True,
        legend=dict(x=1, y=1,
                    xanchor="right",
                    bgcolor=colors['purple2']),
        height=350)

    return title, fig


# update household size graph by local area
@app.callback(
    [Output("size-title", 'children'),
     Output("size_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_size(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = ("Household Size, in " + str(census_year))

    # Create bar graph
    fig = build_bar(size_df,
                    census_year,
                    area,
                    clickData,
                    "Household Size",
                    "Percent of Total Population")

    return title, fig


# update languages table by local area and year
@app.callback(
    [Output("lang-title", 'children'),
     Output("lang_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_lang(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = ("Language Composition, in " + str(census_year))

    # Create table
    fig = build_table(lang, "LANGUAGES", area, census_year, clickData)

    return title, fig


# update ethnicity table by local area and year
@app.callback(
    [Output("eth-title", 'children'),
     Output("eth_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_eth(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = ("Ethnic Composition, in " + str(census_year))

    # Create table
    fig = build_table(eth, "ETHNICITIES", area, census_year, clickData)

    return title, fig


# update housing tenure graph by local area and year
@app.callback(
    [Output("tenure-title", 'children'),
     Output("tenure_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_tenure(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = (str(area) + "'s Housing Tenure Distribution, in " + str(census_year))

    df = get_filter_melt(tenure_df, census_year, area)

    colours = ['forestgreen',
               '#19B1BA']

    fig = go.Figure(
        data=go.Pie(
            labels=df["variable"],
            values=df['value'],
            textinfo='label+percent',
            textfont=dict(
                size=20,
                color="white"),
            hoverinfo="none",
            marker=dict(
                colors=colours,
                line=dict(color='white', width=2)),
            sort=False,
        ),

        layout=go.Layout(
            margin={'l': 0, 'r': 0, 't': 20, 'b': 20},
            plot_bgcolor=colors['purple2'],
        )
    )
    fig.update_layout(
        showlegend=False,
        height=350)

    return title, fig


# update dwelling type graph by local area and year
@app.callback(
    [Output("dwelling-title", 'children'),
     Output("dwelling_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_dwelling(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = ("Distribution of Dwelling Types, in " + str(census_year))

    # Create bar graph
    fig = build_bar(dwel_df,
                    census_year,
                    area,
                    clickData,
                    "Dwelling Type",
                    "Percent of Total Dwellings",
                    range=[0, 95])

    return title, fig


# update transportation graph by local area and year
@app.callback(
    [Output("transport-title", 'children'),
     Output("transport_graph", 'figure')],
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_transport(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    # Set graph title
    title = (
        "Dominant Form of Transportation used by Residents, in " + str(census_year))

    # Create bar graph
    fig = build_bar(trans_df,
                    census_year,
                    area,
                    clickData,
                    "Transportation Type",
                    "Percent of Total Population")

    return title, fig


# update parking graph by local area
@app.callback(
    [Output("parking-title", 'children'),
     Output("parking_graph", 'figure')],
    [Input('van_map', 'clickData')])
def update_parking(clickData):
    latInitial = 49.252
    lonInitial = -123.140
    zoom = 10.7
    df = park.copy()

    # zoom in for selected neighbourhood
    if clickData is not None:
        area = (clickData['points'][0]['location'])
        zoom = 12
        df = park[
            park.LocalArea == area]
        latInitial = list_of_neighbourhoods[
            area]['lat']
        lonInitial = list_of_neighbourhoods[
            area]['lon']
        title = (str(area) + "'s Metered Street Parking, in 2019")
    else:
        title = ("City of Vancouver's Metered Street Parking, in 2019")

    # get count of parking spots
    num = len(df['coord-x'])

    fig = go.Figure(
        data=go.Scattermapbox(
            lat=df['coord-y'],
            lon=df['coord-x'],
            mode="markers",
            hoverinfo="none",
            marker=dict(
                opacity=0.6,
                size=4)
        ),
        layout=go.Layout(
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
            height=350,
            font={"color": "#ffffff"},
        ),
    )

    fig.update_layout(
        annotations=[go.layout.Annotation(
            x=0,
            y=1,
            text=("Street Parking Spots: " + f'{num:,}'),
            showarrow=False,
            font=dict(
                family="sans-serif",
                size=16,
                color="White"),
            bordercolor="Black",
            borderwidth=0,
            borderpad=6,
            bgcolor="rgb(71, 71, 107)",
            opacity=0.7)],
        mapbox=dict(
            center=dict(
                lat=latInitial,
                lon=lonInitial),
            style="carto-positron",
            zoom=zoom,
            bearing=0)
    )

    return title, fig


@app.callback(
    Output('summary_info', 'children'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_side_bar(clickData, year):

    # Get census year and local area
    census_year, area = get_year_area(year, clickData)

    if clickData is not None:
        biz_df = agg_licence[(agg_licence.FOLDERYEAR == year)
                             & (agg_licence.LocalArea == area)]
        biz_num = pd.DataFrame(
            biz_df.groupby(['LocalArea', 'FOLDERYEAR'])[
                'business_id'].sum()).reset_index()
    else:
        biz_df = agg_licence[(agg_licence.FOLDERYEAR == year)]
        biz_num = pd.DataFrame(
            biz_df.groupby(['FOLDERYEAR'])[
                'business_id'].sum()).reset_index()

    # calculate number of businesses
    biz_num = biz_num.business_id[0]

    # Calculate total population
    pop_df = census[['LocalArea', 'Year', 'Age_total']]
    pop_df = pop_df[(pop_df.Year == census_year) & (pop_df.LocalArea == area)]
    pop = int(pop_df.Age_total)

    # Calculate dominant age group
    age = get_filter_melt(age_df, census_year, area)
    age = age[age.value == age.value.max()].reset_index()
    age_frac = age.value[0]
    age_group = age.variable[0]

    # format html output for the summary stats
    sum_info = html.Div(
        children=[
            html.Div(
                className="graph__container fourth",
                children=[
                    html.H6("Vancouver Neighbourhood:",
                            style={"marginBottom": 0}),
                    html.H3(area.upper(),
                            style={"marginTop": 0,
                                   "marginBottom": 0}),
                ], style={"textAlign": "center",
                          "fontFamily": "sans-serif"}
            ),
            html.Div(
                className="graph__container first",
                children=[
                    html.H3(f'{pop:,}', style={"marginBottom": 0}),
                    html.H6("Residents in " + str(census_year)),
                    html.H3(f'{age_frac:.1%}', style={"marginBottom": 0}),
                    html.H6(age_group + " Years of Age",
                            style={"marginTop": 0}),
                    html.H3(f'{biz_num:,}', style={"marginBottom": 0}),
                    html.H6("Businesses in " + str(year)),
                ], style={"textAlign": "center",
                          "fontFamily": "sans-serif",
                          "marginTop": 5}
            )
        ])

    return sum_info


# reset the selections
@app.callback(Output('van_map', 'clickData'),
              [Input('clearButton', 'n_clicks')])
def reset_selection(n_clicks):
    return None


# Create show/hide callbacks for each info modal
for id in ['age', 'size', 'eth', 'lang', 'edu',
           'occ', 'tenure', 'dwelling', 'transport',
           'parking']:
    @app.callback([Output(f"{id}-modal", 'style'),
                   Output(f"{id}-div", 'style')],
                  [Input(f'show-{id}-modal', 'n_clicks'),
                   Input(f'close-{id}-modal', 'n_clicks')])
    def toggle_modal_2(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('show-'):
            return {"display": "block"}, {'zIndex': 1003}
        else:
            return {"display": "none"}, {'zIndex': 0}

########################################
# TAB 3 - UPDATES                      #
########################################


# update map
@app.callback(
    [Output('model-map', 'figure'),
     Output('predict_text1', 'children'),
     Output('predict_text2', 'children')],
    [Input('localarea-dropdown3', 'value'),
     Input('year-slider3', 'value'),
     Input('businesstype-dropdown3', 'value'),
     Input('history-dropdown3', 'value'),
     Input('businessname-input3', 'value'),
     Input('lat-input3', 'value'),
     Input('lon-input3', 'value'),
     Input('fee-input3', 'value'),
     Input('employee-input3', 'value')])
def update_figure3(SelectedLocalArea,
                   SelectedYear,
                   SelectedType,
                   SelectedHistory,
                   InputName,
                   InputLat,
                   InputLon,
                   InputFee,
                   InputEmployee):

    latInitial = 49.250
    lonInitial = -123.121
    zoom = 11

    if (SelectedLocalArea is None) or (
            SelectedYear is None) or (
            SelectedType is None) or (
            SelectedHistory is None) or (
            InputFee is None) or (
            InputEmployee is None):

        return go.Figure(
            data=go.Scattermapbox(),
            layout=go.Layout(
                margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                mapbox=dict(
                    center=dict(
                        lat=latInitial,
                        lon=lonInitial),
                    style="carto-positron",
                    zoom=zoom
                ),
            ),

        ), "Predicted results", ""

    # zoom in for selected neighbourhood
    if SelectedLocalArea:
        zoom = 13
        latInitial = list_of_neighbourhoods[
            SelectedLocalArea]['lat']
        lonInitial = list_of_neighbourhoods[
            SelectedLocalArea]['lon']

    df_tab3 = vis_model[
        (vis_model.FOLDERYEAR == SelectedYear) & (
            vis_model.BusinessType == SelectedType)
    ]

    gpd_tab3 = vis_model_gpd[
        (vis_model_gpd.FOLDERYEAR == SelectedYear) & (
            vis_model_gpd.BusinessType == SelectedType)
    ]

    row = get_census_info(SelectedYear, SelectedLocalArea)
    row['FOLDERYEAR'] = SelectedYear
    row['BusinessType'] = SelectedType
    row['LocalArea'] = SelectedLocalArea
    row['history'] = SelectedHistory
    row['NumberofEmployees'] = InputEmployee
    row['FeePaid'] = InputFee
    row['Parking meters'] = np.mean(vis_model['Parking meters'])
    row['Disability parking'] = np.mean(vis_model['Disability parking'])
    row['nearest_business_count'] = np.nan
    try:
        row['chain'] = vis_model.loc[vis_model.BusinessName ==
                                     InputName, 'chain'].values[0] + 1
    except:
        row['chain'] = 1
    row = pd.DataFrame(row, index=[0])

    # get nearby similar businesses
    if InputLat and InputLon:
        latInitial = InputLat
        lonInitial = InputLon
        zoom = 17
        similar_business_df = get_similar_business(
            Point(InputLat, InputLon), gpd_tab3)
        row.loc[:, 'nearest_business_count'] = len(similar_business_df)

    predict_proba = round(max(model.predict_proba(row)[0]), 4)
    predict = model.predict(row)
    predict_text1 = "Predicted: " + (
        "will renew " if predict == 1 else "will not renew")
    predict_text2 = "Probability: " + str(predict_proba)

    if predict == 1:
        df_tab3 = df_tab3[df_tab3.label == 1]
    else:
        df_tab3 = df_tab3[df_tab3.label == 0]

    if InputLat and InputLon:
        plot_df = similar_business_df
    else:
        plot_df = df_tab3

    # Hover
    customdata = pd.DataFrame({
        'Business Name': plot_df.BusinessName,
        'Business Type': plot_df.BusinessType,
        'Business History': plot_df.history,
        'Actual Label': plot_df.label,
        'Predicted Label': plot_df.predict
    }
    )

    return go.Figure(
        data=go.Scattermapbox(
            lon=plot_df['coord-x'],
            lat=plot_df['coord-y'],
            customdata=customdata,
            marker=dict(
                color=plot_df['predict_proba'],
                showscale=True,
                colorscale="RdBu",
                colorbar=dict(
                    title="Predicted</b><br>Probability"),
            ),
            hovertemplate="""Business Name: %{customdata[0]}</b><br>Business Type: %{customdata[1]}</b><br>Business History: %{customdata[2]}</b><br>Actual Label: %{customdata[3]}</b><br>Predicted Label: %{customdata[4]}<extra></extra>
            """
        ),
        layout=go.Layout(
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
            mapbox=dict(
                center=dict(
                    lat=latInitial,
                    lon=lonInitial),
                style="carto-positron",
                zoom=zoom
            ),
        ),

    ), predict_text1, predict_text2


# Create show/hide callbacks for each info modal
for id in ['model']:
    @app.callback([Output(f"{id}-modal", 'style'),
                   Output(f"{id}-div", 'style')],
                  [Input(f'show-{id}-modal', 'n_clicks'),
                   Input(f'close-{id}-modal', 'n_clicks')])
    def toggle_modal_3(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('show-'):
            return {"display": "block"}, {'zIndex': 1003}
        else:
            return {"display": "none"}, {'zIndex': 0}


app.run_server(debug=True)
