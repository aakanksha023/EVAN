# authors: Jasmine Qin, Keanna Knebel
# date: 2020-06-08

# Basics
import pandas as pd
import geopandas as gpd
import numpy as np
import json

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

df = pd.read_csv("data/processed/census_viz.csv")
licence = pd.read_csv("data/processed/vis_licence.csv")
boundary_df = gpd.read_file("data/raw/local_area_boundary.geojson"
                            ).rename(columns={'name': 'LocalArea'})
agg_licence = pd.read_csv("data/processed/vis_agg_licence.csv")

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

# plotly graph config
config = {'displayModeBar': False, 'scrollZoom': False}

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
                                            'label': str(year),
                                            'style': {'color': 'white'}}
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

    # Dividing the dashboard into tabs
    dcc.Tabs(id="mainTabs", children=[


        # Define the layout of the first Tab
        dcc.Tab(label='BUSINESS LICENCE', children=[
            build_tab1()
        ]),

        # Define the layout of the second Tab
        dcc.Tab(label='NEIGHBOURHOOD PROFILES', children=[

            # main row with map and summary info
            html.Div(
                className='row',
                children=[
                    html.Div(
                        className="app__content",
                        children=[
                            # summary info
                            html.Div(
                                className="one-third column",
                                children=[
                                    html.Div(
                                        id='summary_info',
                                        className="graph__container first"
                                    )
                                ]
                            ),
                            # main map of neighbourhoods
                            html.Div(
                                className="two-thirds column map__slider__container",
                                children=[
                                    # map
                                    dcc.Graph(
                                        id='van_map',
                                        style={"visibility": "visible"},
                                        config=config),

                                    # slider
                                    html.Div(
                                        className='div-for-slider',
                                        children=[
                                            dcc.Slider(
                                                id='year_slider_census',
                                                min=licence['FOLDERYEAR'].min(),
                                                max=licence['FOLDERYEAR'].max(),
                                                value=2016,
                                                marks={str(year): {
                                                    'label': str(year),
                                                    'style': {'color': 'white'}}
                                                for year in licence['FOLDERYEAR'].unique()},
                                                step=None
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ],
                style={'marginTop': 50}

            ),

            # Adding tabs for summary neighbourhood data
            dcc.Tabs(id="subTabs", children=[

                # summary of local demographics
                dcc.Tab(label='PEOPLE', children=[

                    html.Div(
                        className="app__content",
                        children=[
                            # population by age
                            html.Div(
                                className="one-half-tab2 column bottom__box__tab2",
                                children=[
                                    html.H4('Age Distribution',
                                            style={"textAlign": "center"}),
                                    dcc.Graph(id='age_graph',
                                              config=config)
                                ], ),
                            # population by household size
                            html.Div(
                                className="other-half-tab2 column bottom__box__tab2",
                                children=[
                                    html.H4('Household Size',
                                            style={"textAlign": "center"}),
                                    dcc.Graph(id='size_graph',
                                              config=config)
                                ])
                        ], style={'marginTop': 50}),

                    # population by language
                    html.Div(
                        className="app__content",
                        children=[
                            html.Div(
                                className="one-half column",
                                children=[
                                    html.H4('Language Composition',
                                            style={"textAlign": "center"}),
                                    dcc.Graph(id='lang_table',
                                              config=config)
                                ]
                            ),
                            html.Div(
                                className="other-half column",
                                children=[
                                    html.H4('Ethnic Composition',
                                            style={"textAlign": "center"}),
                                    dcc.Graph(id='eth_table',
                                              config=config)]
                            )
                        ], style={'marginTop': 50}
                    ),

                    # population by education level
                    html.Div(
                        className="app__content",
                        children=[
                            html.Div(
                                className="one-half column",
                                children=[
                                    html.H4('Education Level',
                                            style={"textAlign": "center"}),
                                    dcc.Graph(id='edu_graph',
                                              config=config,
                                              style={"width": "80%"})
                                ]),
                            html.Div(
                                className="other-half column",
                                children=[
                                    html.H5('text description...')
                                ])
                        ], style={'marginTop': 50}),
                    ]),

                # summary of local business structure
                dcc.Tab(label='BUSINESSES', children=[

                ]),

                # summary of local infrastructure
                dcc.Tab(label='INFRASTRUCTURE', children=[

                ]),

            ], style={'marginTop': 50}),
        ]),

        # Define the layout of the third Tab
        #dcc.Tab(label='Sources')
    ]),

    # main app footer
    html.Footer([

        html.H4("PROJECT PARTNERS", style={
                "textAlign": "center", 'marginBottom': 50}),
        dbc.Row([
            dbc.Col([
                html.Img(
                    src="https://brand3.sites.olt.ubc.ca/files/2018/09/5NarrowLogo_ex_768.png",
                    style={"width": "20%"})
                    ],
                    width=4,
                    align='end'),
            dbc.Col([
                html.Img(
                    src="https://deetken.com/wp-content/uploads/2019/02/logo-1.png",
                    style={"width": "20%"})
                    ],
                    width=4)
                ], justify="center"),
    ], style={'marginTop': 200}),
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
        margin=dict(l=0, r=0, b=0, t=0),
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

    x_title = "Count of Unique Businesses"

    return go.Figure(
        data=go.Bar(x=histogram_df['x-axis'],
                    y=histogram_df['y-axis'],
                    orientation='h',
                    marker_color=colors['green3'],
                    hoverinfo='x'
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
    [Input("industry-dropdown", "value"),
     Input("localarea-dropdown", "value")],
)
def update_line(SelectedIndustry, SelectedLocalArea):
    if SelectedIndustry or SelectedLocalArea:
        if SelectedIndustry and SelectedLocalArea:
            line_df = agg_licence[
                agg_licence.BusinessIndustry == SelectedIndustry]
            line_df = line_df[line_df.LocalArea == SelectedLocalArea]
        elif SelectedIndustry:
            line_df = agg_licence[
                agg_licence.BusinessIndustry == SelectedIndustry]
        else:
            line_df = agg_licence[
                agg_licence.LocalArea == SelectedLocalArea]

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

###############################################################################
# second tab updates


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
                                         'selected': colors['purple5'],
                                         'blank': colors['purple4']},
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


# update education graph by local area
@app.callback(
    Output('edu_graph', 'figure'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_edu(clickData, year):
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
        area = 'Metro Vancouver'

    edu_df = df[['LocalArea', 'Year',
                 'No certificate/diploma',
                 'High school',
                 'Apprenticeship/Trades',
                 'College',
                 'University']]

    van_df = edu_df.copy()
    edu_df = edu_df[(edu_df.Year == census_year) & (edu_df.LocalArea == area)]
    edu_df = edu_df.melt(id_vars=['LocalArea', 'Year'],
                         var_name='Education',
                         value_name='Percent of Total Population')

    edu_fig = go.Figure(
        data=go.Bar(
                    x=edu_df["Education"],
                    y=edu_df['Percent of Total Population']*100,
                    name=area,
                    marker_color='#19B1BA',
                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>"),
        layout=go.Layout(
                    margin=dict(l=10, r=10, b=10, t=10),
                    template='simple_white'))

    if clickData is not None:
        van_df = van_df[(
            van_df.Year == census_year) & (van_df.LocalArea == 'Metro Vancouver')]
        van_df = van_df.melt(id_vars=['LocalArea', 'Year'],
                             var_name='Education',
                             value_name='Percent of Total Population')

        edu_fig.add_trace(
            go.Bar(
               x=van_df["Education"],
               y=van_df['Percent of Total Population']*100,
               name='Metro Vancouver',
               marker_color='#afb0b3',
               hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
            ))

    edu_fig.update_layout(
        barmode='group',
        yaxis={'title':"Percent of Total Population"},
        xaxis_title="Level of Education",
        showlegend=True,
        legend=dict(x=1, y=1, xanchor="right"),
        height=300)

    return edu_fig


# update age graph by local area
@app.callback(
    Output('age_graph', 'figure'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_age(clickData, year):
    # select nearest census year
    if year <= 2003:
        census_year = 2001
    elif year <= 2008:
        census_year = 2006
    elif year <= 2013:
        census_year = 2011
    else:
        census_year = 2016

    area = 'Metro Vancouver'

    if clickData is not None:
        area = (clickData['points'][0]['location'])

    age_df = df[['LocalArea', 'Year',
                 'Under 20',
                 '20 to 34',
                 '35 to 44',
                 '45 to 54',
                 '55 to 64',
                 '65 to 79',
                 '80 and Older']]
    van_df = age_df.copy()
    age_df = age_df[(age_df.Year == census_year) & (age_df.LocalArea == area)]
    age_df = age_df.melt(id_vars=['LocalArea', 'Year'],
                         var_name='Age',
                         value_name='Population')

    age_fig = go.Figure(
                data=go.Scatter(
                    x=age_df['Age'],
                    y=age_df['Population']*100,
                    mode='lines+markers',
                    marker=dict(
                        color='#19B1BA',
                        size=8),
                    name=area,
                    line=dict(width=4),
                    line_shape='spline',
                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>"),

                layout=go.Layout(
                    margin=dict(l=10, r=10, b=10, t=10),
                    template='simple_white',
                    plot_bgcolor=colors['purple2']))

    if clickData is not None:
        van_df = van_df[(
            van_df.Year == census_year) & (van_df.LocalArea == 'Metro Vancouver')]
        van_df = van_df.melt(id_vars=['LocalArea', 'Year'],
                             var_name='Age',
                             value_name='Population')
        age_fig.add_trace(
            go.Scatter(
                    x=van_df['Age'],
                    y=van_df['Population']*100,
                    mode='lines+markers',
                    marker=dict(
                        color='#afb0b3',
                        size=8),
                    name='Metro Vancouver',
                    line=dict(width=3),
                    line_shape='spline',
                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))

    age_fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Percent of Total Population",
        showlegend=True,
        legend=dict(x=1, y=1,
                    xanchor="right",
                    bgcolor=colors['purple2']),
        height=300)

    return age_fig


# update household size graph by local area
@app.callback(
    Output('size_graph', 'figure'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_size(clickData, year):
    area = 'Metro Vancouver'
    # select nearest census year
    if year <= 2003:
        census_year = 2001
    elif year <= 2008:
        census_year = 2006
    elif year <= 2013:
        census_year = 2011
    else:
        census_year = 2016

    if clickData is not None:
        area = (clickData['points'][0]['location'])
    size_df = df[['LocalArea',
                  'Year',
                  '1 person',
                  '2 persons',
                  '3 persons',
                  '4 to 5 persons',
                  '6+ persons']]
    van_df = size_df.copy()
    size_df = size_df[(size_df.Year == census_year) & (size_df.LocalArea == area)]
    size_df = size_df.melt(id_vars=['LocalArea', 'Year'],
                           var_name='Household Size',
                           value_name='Percent of Total Population')

    size_fig = go.Figure(
        data=go.Bar(
                    x=size_df["Household Size"],
                    y=size_df['Percent of Total Population']*100,
                    name=area,
                    marker_color='#19B1BA',
                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>"),
        layout=go.Layout(
                    margin=dict(l=10, r=10, b=10, t=10),
                    template='simple_white',
                    plot_bgcolor=colors['purple2']))

    if clickData is not None:
        van_df = van_df[(
            van_df.Year == census_year) & (van_df.LocalArea == 'Metro Vancouver')]
        van_df = van_df.melt(id_vars=['LocalArea', 'Year'],
                             var_name='Household Size',
                             value_name='Percent of Total Population')

        size_fig.add_trace(
            go.Bar(
               x=van_df["Household Size"],
               y=van_df['Percent of Total Population']*100,
               name='Metro Vancouver',
               marker_color='#afb0b3',
               hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
            ))

    size_fig.update_layout(
        barmode='group',
        xaxis_title="Household Size",
        yaxis_title="Percent of Total Population",
        showlegend=True,
        legend=dict(x=1, y=1, xanchor="right",
                    bgcolor=colors['purple2']),
        height=300)

    return size_fig

# update languages table by local area and year
@app.callback(
    Output('lang_table', 'figure'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_lang(clickData, year):
    # select nearest census year
    if year <= 2003:
        census_year = 2001
    elif year <= 2008:
        census_year = 2006
    elif year <= 2013:
        census_year = 2011
    else:
        census_year = 2016

    lang = df[['LocalArea', 'Year', 'English', 'French',
               'Chinese languages', 'Tagalog (Filipino)',
               'Panjabi (Punjabi)', 'Italian', 'German',
               'Spanish', 'Vietnamese', 'Korean language',
               'Hindi', 'Persian (Farsi)']]
    lang = lang.rename(columns={'Chinese languages': 'Chinese',
                                'Korean language': 'Korean'})

    # update local area
    if clickData is not None:
        area = (clickData['points'][0]['location'])
    else:
        area = 'Metro Vancouver'

    # filter data frame by area and year
    lang = lang[(lang.Year == census_year) & (lang.LocalArea.isin([area, 'Metro Vancouver']))]
    lang.drop(columns=['Year'], inplace=True)
    lang.set_index('LocalArea', inplace=True)
    lang = lang.T

    # select the top 5 most common languages
    lang = lang.sort_values(by=[area], ascending=False)
    lang.reset_index(inplace=True)
    lang = lang[0:5].copy()

    if clickData is not None:
        # format results in table
        table = go.Figure(
            data=[
                go.Table(
                        header=dict(
                            values=['LANGUAGES',
                                     area.upper(),
                                     'METRO VANCOUVER'],
                            fill_color=colors['purple4'],
                            align=['center'],
                            font=dict(color='white', size=22),
                            height=40),
                        cells=dict(values=[lang['index'],
                                           round(lang[area]*100, 2),
                                           round(lang['Metro Vancouver']*100, 2)],
                            fill=dict(color=['white']),
                            align=['center'],
                            font_size=20,
                            height=35)
                )
            ]
        )
    else:
        # format results in table
        table = go.Figure(
            data=[
                go.Table(
                        header=dict(
                            values=['LANGUAGES', area.upper()],
                            fill_color=colors['purple4'],
                            align=['center'],
                            font=dict(color='white', size=22),
                            height=40),
                        cells=dict(values=[lang['index'], round(lang[area]*100, 2)],
                            fill=dict(color=['white']),
                            align=['center'],
                            font_size=20,
                            height=35)
                )
            ]
        )

    return table

# update languages table by local area and year
@app.callback(
    Output('eth_table', 'figure'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_eth(clickData, year):
    # select nearest census year
    if year <= 2003:
        census_year = 2001
    elif year <= 2008:
        census_year = 2006
    elif year <= 2013:
        census_year = 2011
    else:
        census_year = 2016

    eth = df[['LocalArea', 'Year', 'Caucasian', 'Arab', 'Black',
              'Chinese', 'Filipino', 'Japanese', 'Korean',
              'Latin American', 'West Asian', 'South Asian',
              'Southeast Asian']]

    # update local area
    if clickData is not None:
        area = (clickData['points'][0]['location'])
    else:
        area = 'Metro Vancouver'

    # filter data frame by area and year
    eth = eth[(eth.Year == census_year) & (eth.LocalArea.isin([area, 'Metro Vancouver']))]
    eth.drop(columns=['Year'], inplace=True)
    eth.set_index('LocalArea', inplace=True)
    eth = eth.T

    # select the top 5 most common ethnicities
    eth = eth.sort_values(by=[area], ascending=False)
    eth.reset_index(inplace=True)
    eth = eth[0:5].copy()

    if clickData is not None:
        # format results in table
        table = go.Figure(
            data=[
                go.Table(
                        header=dict(
                            values=['ETHNICITIES',
                                     area.upper(),
                                     'METRO VANCOUVER'],
                            fill_color=colors['purple4'],
                            align=['center'],
                            font=dict(color='white', size=22),
                            height=40),
                        cells=dict(values=[eth['index'],
                                           round(eth[area]*100, 2),
                                           round(eth['Metro Vancouver']*100, 2)],
                            fill=dict(color=['white']),
                            align=['center'],
                            font_size=20,
                            height=35)
                )
            ]
        )
    else:
        # format results in table
        table = go.Figure(
            data=[
                go.Table(
                        header=dict(
                            values=['ETHNICITIES', area.upper()],
                            fill_color=colors['purple4'],
                            align=['center'],
                            font=dict(color='white', size=22),
                            height=40),
                        cells=dict(values=[eth['index'], round(eth[area]*100, 2)],
                            fill=dict(color=['white']),
                            align=['center'],
                            font_size=20,
                            height=35)
                )
            ]
        )

    return table

@app.callback(
    Output('summary_info', 'children'),
    [Input('van_map', 'clickData'),
     Input('year_slider_census', 'value')])
def update_side_bar(clickData, year):
    # select nearest census year
    if year <= 2003:
        census_year = 2001
    elif year <= 2008:
        census_year = 2006
    elif year <= 2013:
        census_year = 2011
    else:
        census_year = 2016

    if clickData is not None:
        area = (clickData['points'][0]['location'])
        biz_df = agg_licence[(agg_licence.FOLDERYEAR == year) & (agg_licence.LocalArea == area)]
        biz_num = pd.DataFrame(
        biz_df.groupby(['LocalArea', 'FOLDERYEAR'])[
            'business_id'].sum()).reset_index()
    else:
        area = 'Metro Vancouver'
        biz_df = agg_licence[(agg_licence.FOLDERYEAR == year)]
        biz_num = pd.DataFrame(
        biz_df.groupby(['FOLDERYEAR'])[
            'business_id'].sum()).reset_index()

    #biz_df = pd.DataFrame(
      #  biz_df.groupby(['BusinessIndustry'])[
       #     'business_id'].sum()).reset_index()
    #biz = biz_df[biz_df.business_id == biz_df.business_id.max()].reset_index()
    #biz = biz_df.BusinessIndustry[0]

    # calculate number of businesses
    biz_num = biz_num.business_id[0]

    # calculate total population
    pop_df = df[['LocalArea', 'Year', 'Age_total']]
    pop_df = pop_df[(pop_df.Year == census_year) & (pop_df.LocalArea == area)]
    pop = int(pop_df.Age_total)

    # calculate dominate age group
    age_df = df[['LocalArea', 'Year',
                 'Under 20',
                 '20 to 34',
                 '35 to 44',
                 '45 to 54',
                 '55 to 64',
                 '65 to 79',
                 '80 and Older']]
    age_df = age_df[(age_df.Year == census_year) & (age_df.LocalArea == area)]
    age_df = age_df.melt(id_vars=['LocalArea', 'Year'],
                         var_name='Age',
                         value_name='Population')
    age = age_df[age_df.Population == age_df.Population.max()].reset_index()
    age_frac = age.Population[0]
    age_group = age.Age[0]

    # format html output for the summary stats
    sum_info = html.Div(
        children=[
            html.H6("Vancouver Neighbourhood:",
                    style={"marginBottom": 0}),
            html.H3(area.upper(), style={"marginTop": 0}),
            html.H3(f'{pop:,}', style={"marginBottom": 0}),
            html.H6("Residents in " + str(census_year)),
            html.H3(f'{age_frac:.1%}', style={"marginBottom": 0}),
            html.H6(age_group + " Years of Age", style={"marginTop": 0}),
            html.H3(f'{biz_num:,}', style={"marginBottom": 0}),
            html.H6("Businesses in " + str(year)),
            ], style={"textAlign": "center",
                      "fontFamily": "sans-serif"})

    return sum_info


app.run_server(debug=True)