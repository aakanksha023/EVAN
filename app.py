# authors: Jasmine Qin, Keanna Knebel
# date: 2020-06-08

# Basics
import pandas as pd
import geopandas as gpd
import numpy as np
import json
import re

# Plotly
import plotly.graph_objects as go
import plotly.express as px

# Dash
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

##########
# Set-up #
##########

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoiamFzbWluZXF5aiIsImEiOiJja2Fy\
c2toN2Ewb3FxMnJsZzhuN3N3azk2In0.SJcixuEa_agNUDz7fFYDEg"

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#############
# Read data #
#############

licence = pd.read_csv("data/processed/vis_licence.csv")
boundary_df = gpd.read_file("data/raw/local_area_boundary.geojson"
                            ).rename(columns={'name': 'LocalArea'})

with open("data/raw/local_area_boundary.geojson") as f:
    boundary = json.load(f)

for i in boundary['features']:
    i['name'] = i['properties']['name']
    i['id'] = i['properties']['mapid']

######################
# Info and wrangling #
######################

licence = licence[licence.Status == 'Issued']

industries = licence.BusinessIndustry.unique()
localareas = boundary_df.LocalArea.unique()

list_of_neighbourhoods = {
    'Arbutus-Ridge': {'lat': 49.1527, 'lon': -123.1028},
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

# wrangle for choropleth (unused)
number_of_businesses = licence.groupby(
    'LocalArea')['BusinessName'].apply(
    lambda x: np.log(len(x.unique())))
boundary_df = boundary_df.merge(pd.DataFrame(
    number_of_businesses).reset_index(), how="left", on='LocalArea')

colors = {
    'purple5': 'rgb(71, 71, 107)',
    'purple4': 'rgb(163, 163, 194)',
    'purple2': 'rgb(240, 240, 245)',
    'green3': 'rgb(117, 163, 129)'
}

##########
# Layout #
##########

# Licence visualization layout


def build_tab1():
    return html.Div(
        className='row',
        children=[
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
                                                    "border": "0px solid black"},
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
                                                    "border": "0px solid black"},
                                                placeholder='Select a neighbourhood'
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
                                            'label': str(year), 'style': {
                                                'color': 'white'}}
                                               for year in licence['FOLDERYEAR'].unique()},
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
                        className="one-half column bottom__box",
                        children=[
                            # graph title
                            html.Div(
                                [html.H6(id='histogram-title',
                                         className="graph__title")]
                            ),


                            dcc.Graph(id="business-type-histogram",
                                      config={'displayModeBar': False}),
                        ]
                    ),

                    # business industry by year
                    html.Div(
                        className="other-half column bottom__box",
                        children=[
                            # graph title
                            html.Div(
                                [html.H6(id='line-title',
                                         className="graph__title")]
                            ),

                            dcc.Graph(id="business-industry-line",
                                      config={'displayModeBar': False})
                        ],
                    ),
                ],
            ),
        ]
    )


# Main layout
app.layout = html.Div([

    # Main app header
    html.Div([
        # Setting the main title of the Dashboard
        html.H1("Forecasting the Evolution of Vancouver's Business Landscape",
                style={"textAlign": "center", 'fontFamily': 'arial',
                       'marginTop': 50, 'marginBottom': 50,
                       'marginLeft': 100, 'marginRight': 100})],
             style={'Color': '#2E4053'}),

    # Dividing the dashboard in 3 tabs
    dcc.Tabs(id="mainTabs", children=[


        # Define the layout of the first Tab
        dcc.Tab(label='Business Licence', children=[
            build_tab1()
        ]),

        # Define the layout of the second Tab
        dcc.Tab(label='Neighbourhood Profiles', children=[

            # neighbourhood tab header
            html.Div([
                html.H2("VANCOUVER NEIGHBOURHOODS",
                        style={"textAlign": "center"}),
                html.H6("Click the map to explore Vancouver Neighbourhoods",
                        style={"textAlign": "center"})],
                     style={'marginTop': 50}),

            # main map of neighbourhoods
            #dcc.Graph(figure=choro, config=config),

            # Adding tabs for summary neighbourhood data
            dcc.Tabs(id="subTabs", children=[

                # summary of local demographics
                dcc.Tab(label='People', children=[

                ]),

                # summary of local business structure
                dcc.Tab(label='Businesses', children=[

                ])

            ], style={'marginTop': 50}),
        ]),

        # Define the layout of the third Tab
        dcc.Tab(label='Sources')
    ]),

    # main app footer
    html.Footer([

        html.H4("PROJECT PARTNERS", style={
                "textAlign": "center", 'marginBottom': 50}),
        dbc.Row([
            dbc.Col([
                html.Img(src="https://brand3.sites.olt.ubc.ca/files/2018/09/5NarrowLogo_ex_768.png",
                         style={"width": "20%"})],
                    width=4, align='end'),
            dbc.Col([
                html.Img(src="https://deetken.com/wp-content/uploads/2019/02/logo-1.png",
                         style={"width": "20%"})],
                    width=4)
        ], justify="center"),
    ], style={'marginTop': 300}),
])

###########
# Updates #
###########

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
                            'selected': colors['purple5'],
                            'blank': colors['purple4']},
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
        margin=dict(
            l=0, r=0, b=0, t=0,
        ),
        coloraxis_showscale=False,
        showlegend=False)


# update histogram
@app.callback(
    Output("business-type-histogram", "figure"),
    [Input("industry-dropdown", "value")],
)
def update_histogram(SelectedIndustry):
    if SelectedIndustry:
        histogram_df = licence[licence.BusinessIndustry == SelectedIndustry]
        histogram_df = histogram_df[histogram_df.Status == "Issued"]

        histogram_df = histogram_df[
            ~(histogram_df.BusinessType.str.contains(r'\*Historic\*'))]
        histogram_df = pd.DataFrame(
            histogram_df.groupby(['BusinessType'])[
                'BusinessName'].count()).reset_index()
        histogram_df = histogram_df.sort_values(
            'BusinessName')

        histogram_df = histogram_df.rename(
            columns={'BusinessType': 'y-axis',
                     'BusinessName': 'x-axis'}
        )

        x_title = "Count of Unique Businesses in " + SelectedIndustry

    else:
        histogram_df = licence[licence.Status == "Issued"]
        histogram_df = pd.DataFrame(
            histogram_df.groupby(['BusinessIndustry'])[
                'BusinessName'].count()).reset_index()
        histogram_df = histogram_df.sort_values(
            'BusinessName')

        histogram_df = histogram_df.rename(
            columns={'BusinessIndustry': 'y-axis',
                     'BusinessName': 'x-axis'}
        )

        x_title = "Count of Unique Businesses"

    return go.Figure(
        data=go.Bar(x=histogram_df['x-axis'],
                    y=histogram_df['y-axis'],
                    orientation='h',
                    marker_color=colors['green3']
                    ),
        layout=go.Layout(
            margin=dict(l=10, r=10, b=20, t=10),
            annotations=[
                dict(
                    x=xi,
                    y=yi,
                    text=yi,
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(color=colors['purple5']),
                )
                for xi, yi in zip(histogram_df['x-axis'],
                                  histogram_df['y-axis'])
            ],
            xaxis=go.XAxis(
                title=x_title),
            yaxis=go.XAxis(
                showticklabels=False),
            plot_bgcolor=colors['purple2'],
        )
    )


# update line
@app.callback(
    Output("business-industry-line", "figure"),
    [Input("industry-dropdown", "value")],
)
def update_line(SelectedIndustry):
    if SelectedIndustry:
        line_df = licence[licence.BusinessIndustry == SelectedIndustry]

        line_df = pd.DataFrame(line_df.groupby([
            'FOLDERYEAR'])['BusinessName'].count()).reset_index()

        y_title = "Count of Unique Businesses in " + SelectedIndustry

    else:
        line_df = pd.DataFrame(licence.groupby([
            'FOLDERYEAR'])['BusinessName'].count()).reset_index()

        y_title = "Count of Unique Businesses"

    line_df = line_df.sort_values('FOLDERYEAR')

    return go.Figure(
        data=go.Scatter(x=line_df['FOLDERYEAR'],
                        y=line_df['BusinessName'],
                        mode='lines+markers',
                        marker_color=colors['green3']),

        layout=go.Layout(
            margin=dict(l=10, r=10, b=10, t=10),
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
     Input("localarea-dropdown", "value")])
def update_figure(SelectedIndustry,
                  SelectedYear,
                  SelectedLocalArea):
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
                    hovertemplate="""Business Name: %{customdata[0]}</b><br>Business Type: %{customdata[1]}"""
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
                    hovertemplate="""Business Name: %{customdata[0]}</b><br>Business Type: %{customdata[1]}"""
                )
            )

    return go.Figure(

        data=traces,

        layout=go.Layout(
            margin=go.layout.Margin(l=0, r=0, t=0, b=0),
            legend=dict(
                x=0,
                y=1,
                bordercolor="Black",
                borderwidth=0,
                bgcolor="rgb(71, 71, 107)",
                font=dict(
                    family="sans-serif",
                    size=12
                ),
                orientation="h"
            ),
            font={"color": "#ffffff"},
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(
                    lat=latInitial,
                    lon=lonInitial),
                style="dark",
                zoom=zoom,
                bearing=0
            ),
        )
    )


app.run_server(debug=True)
