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
        ]
    )

app = dash.Dash(__name__)
app.layout = get_layout
app.config['suppress_callback_exceptions']=True

if __name__ == "__main__":
    app.run_server(port=8025, debug=False)
