import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from datetime import datetime, date, timedelta
import json, csv, dash_table, time, operator
from connect import norm_records, rec_lows, rec_highs, all_temps
import pandas as pd
import numpy as np
from numpy import arange,array,ones
from scipy import stats 
import psycopg2

df_all_temps = pd.DataFrame(all_temps,columns=['dow','sta','Date','TMAX','TMIN'])

df_norms = pd.DataFrame(norm_records)

df_rec_lows = pd.DataFrame(rec_lows)

df_rec_highs = pd.DataFrame(rec_highs)

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")
startyr = 1950
year_count = current_year-startyr

def get_layout():
    return html.Div(
        [
           html.Div([
                html.H4(
                    'DENVER TEMPERATURE RECORD',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div(
                    'NOAA Stapleton Station Data',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Label('Select Product'),
                    dcc.RadioItems(
                        id='product',
                        options=[
                            {'label':'Temperature graphs', 'value':'temp-graph'},
                            {'label':'Climatology for a day', 'value':'climate-for-day'},
                            {'label':'Full Record Bar Graphs', 'value':'frbg'},
                            {'label':'5 Year Moving Avgs', 'value':'fyma-graph'},
                            {'label':'Full Record Heat Map', 'value':'frhm'},
                        ],
                        # value='temp-graph',
                        labelStyle={'display': 'inline'},
                    ),
                ],
                    className='twelve columns'
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(
                            id='year-picker'
                        ),
                        html.Div(
                            id='fyma-params'
                        ),
                        html.Div(
                            id='date-picker'
                        ),
                    ],
                        className='four columns'
                    ),
                ],
                    className='row'
                ),
            ],
                className='pretty_container', style={'height': '25px'}
            ),
        ]
    )

app = dash.Dash(__name__)
app.layout = get_layout
app.config['suppress_callback_exceptions']=True

@app.callback(
    Output('date-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
def display_date_selector(product_value):
    if product_value == 'climate-for-day':
        return  html.Div([
            html.Div([
                html.P('Select Date (MM-DD)'),
            ],
                className='six columns'
            ),
             dcc.DatePickerSingle(
                    id='date',
                    display_format='MM-DD',
                    date=today
            )
        ],
            className='row'
        ),
        

@app.callback(
    Output('year-picker', 'children'),
    [Input('product', 'value')])
def display_year_selector(product_value):
    if product_value == 'temp-graph':
        return html.Div([
            html.Div([
                html.P('Enter Year (YYYY)'),
            ],
                className='six columns'
            ),
            dcc.Input(
                id = 'year',
                type = 'number',
                value = str(current_year),
                min = 1950, 
                max = current_year
            ),
        ],
            className='row'
        ),
    elif product_value == 'fyma-graph':
        return html.Div([
            dcc.RadioItems(
                    id = 'fyma-param',
                    options = [
                        {'label':'Max Temp', 'value':'TMAX'},
                        {'label':'Min Temp', 'value':'TMIN'},
                    ],
                    # value = 'TMAX',
                    labelStyle = {'display':'inline-block'}
                )
        ],
        ),

if __name__ == "__main__":
    app.run_server(port=8025, debug=False)
