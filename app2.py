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
                            id='params'
                        ),
                    ],
                        className='twelve columns'
                    ),
                ],
                    className='row'
                ),
            ],
                className='pretty_container', style={'height': '25px'}
            ),
            html.Div([
                html.Div([
                    html.Div(
                        id='graph'
                    ),
                ],
                    className='eight columns'
                ),
                html.Div([
                    html.Div([
                        html.Div(id='graph-stats'
                        ),
                    ],
                    ),
                    html.Div([
                        html.Div(id='frs-bar-controls'
                        ),
                    ],
                    ),
                    html.Div([
                        html.Div(id='frs-heat-controls'
                        ),
                    ],
                    ),
                    html.Div([
                        html.Div(id='fyma-stats'
                        ),
                    ],
                    ),
                ],
                    className='four columns'
                ),    
            ],
                className='row'
            ),
            html.Div(id='all-data', style={'display': 'none'}),
            html.Div(id='rec-highs', style={'display': 'none'}),
            html.Div(id='rec-lows', style={'display': 'none'}),
            html.Div(id='norms', style={'display': 'none'}),
            html.Div(id='temp-data', style={'display': 'none'}),
            html.Div(id='df5', style={'display': 'none'}),
            html.Div(id='max-trend', style={'display': 'none'}),
            html.Div(id='min-trend', style={'display': 'none'}),
            html.Div(id='d-max-max', style={'display': 'none'}),
            html.Div(id='avg-of-dly-highs', style={'display': 'none'}),
            html.Div(id='d-min-max', style={'display': 'none'}),
            html.Div(id='d-min-min', style={'display': 'none'}),
            html.Div(id='avg-of-dly-lows', style={'display': 'none'}),
            html.Div(id='d-max-min', style={'display': 'none'}),
            html.Div(id='temps', style={'display': 'none'}),
        ]
    )

app = dash.Dash(__name__)
app.layout = get_layout
app.config['suppress_callback_exceptions']=True

@app.callback(
    Output('graph-stats', 'children'),
    [Input('temps', 'children'),
    Input('product','value')])
def display_graph_stats(temps, selected_product):
    temps = pd.read_json(temps)
    temps.index = pd.to_datetime(temps.index, unit='ms')
    temps = temps[np.isfinite(temps['TMAX'])]
    day_count = temps.shape[0]
    rec_highs = len(temps[temps['TMAX'] == temps['rh']])
    rec_lows = len(temps[temps['TMIN'] == temps['rl']])
    days_abv_norm = len(temps[temps['TMAX'] > temps['nh']])
    days_blw_norm = len(temps[temps['TMIN'] < temps['nl']])
    nh = temps['nh'].sum()
    nl = temps['nl'].sum()
    tmax = temps['TMAX'].sum()
    tmin = temps['TMIN'].sum()
    # nh_sum = temps['nh'][-31:].sum()
    # nh_sum2 = temps['nh'][:60].sum()

    degree_days = ((temps['TMAX'].sum() - temps['nh'].sum()) + (temps['TMIN'].sum() - temps['nl'].sum())) / 2
    if degree_days > 0:
        color = 'red'
    elif degree_days < 0:
        color = 'blue'
    if selected_product == 'temp-graph':
        return html.Div(
            [
                html.Div([
                    html.Div('Day Count', style={'text-align':'center'}),
                    html.Div('{}'.format(day_count), style={'text-align': 'center'})
                ],
                    className='round1'
                ),
                    html.Div([
                        html.Div('Records', style={'text-align':'center'}),
                        html.Div([
                            html.Div([
                                html.Div('High: {}'.format(rec_highs), style={'text-align': 'center', 'color':'red'}),
                            ],
                                className='six columns'
                            ),
                            html.Div([
                                html.Div('Low: {}'.format(rec_lows), style={'text-align': 'center', 'color':'blue'})
                            ],
                                className='six columns'
                            ),
                        ],
                            className='row'
                        ),
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('Days Above/Below Normal', style={'text-align':'center'}),
                        html.Div([
                            html.Div([
                                html.Div('Above: {}'.format(days_abv_norm), style={'text-align': 'center', 'color':'red'}),
                            ],
                                className='six columns'
                            ),
                            html.Div([
                                html.Div('Below: {}'.format(days_blw_norm), style={'text-align': 'center', 'color':'blue'})
                            ],
                                className='six columns'
                            ),
                        ],
                            className='row'
                        ),
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('Degree Days Over/Under Normal', style={'text-align':'center'}),
                        html.Div(html.Div('{:.0f} Degree Days'.format(degree_days), style={'text-align': 'center', 'color':color})),
                    ],
                        className='round1'
                    ),     
            ],
                className='round1'
            ),

@app.callback([Output('graph1', 'figure'),
             Output('temps', 'children')],
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('norms', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs, rec_lows, norms, selected_year, period):
    previous_year = int(selected_year) - 1
    selected_year = selected_year
    temps = pd.read_json(temp_data)
    temps = temps.drop([0,1], axis=1)
    temps.columns = ['date','TMAX','TMIN']
    temps['date'] = pd.to_datetime(temps['date'], unit='ms')
    temps = temps.set_index(['date'])
    temps['dif'] = temps['TMAX'] - temps['TMIN']
    
    temps_cy = temps[(temps.index.year==selected_year)]
    temps_py = temps[(temps.index.year==previous_year)][-31:]
   
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_highs_ly = df_record_highs_ly.set_index(1)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_record_lows_ly = df_record_lows_ly.set_index(1)
    df_rl_cy = df_record_lows_ly[:len(temps_cy.index)]
    df_rh_cy = df_record_highs_ly[:len(temps_cy.index)]

    df_norms = pd.read_json(norms)
    if selected_year % 4 == 0:
        df_norms = df_norms
    else:
        df_norms = df_norms.drop(df_norms.index[59])
    df_norms_cy = df_norms[:len(temps_cy.index)]
    df_norms_py = df_norms[:31]
   
  
    temps_cy.loc[:,'rl'] = df_rl_cy[0].values
    temps_cy.loc[:,'rh'] = df_rh_cy[0].values
    temps_cy.loc[:,'nh'] = df_norms_cy[3].values
    temps_cy.loc[:,'nl'] = df_norms_cy[4].values
   
    temps_py.loc[:,'nh'] = df_norms_py[3].values
    temps_py.loc[:,'nl'] = df_norms_py[4].values
   
    if period == 'spring':
        temps = temps_cy[temps_cy.index.month.isin([3,4,5])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index
      
    elif period == 'summer':
        temps = temps_cy[temps_cy.index.month.isin([6,7,8])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'fall':
        temps = temps_cy[temps_cy.index.month.isin([9,10,11])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'winter':
        date_range = []
        date_time = []
        sdate = date(int(previous_year), 12, 1)
        edate = date(int(selected_year), 12, 31)

        delta = edate - sdate

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            date_range.append(day)
        for j in date_range:
            day = j.strftime("%Y-%m-%d")
            date_time.append(day)

        temps_py = temps_py[temps_py.index.month.isin([12])]
        temps_cy = temps_cy[temps_cy.index.month.isin([1,2])]
        temp_frames = [temps_py, temps_cy]
        temps = pd.concat(temp_frames, sort=True)
        date_time = date_time[:91]  
        
        df_record_highs_jan_feb = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_highs_dec = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(12-)')]
        high_frames = [df_record_highs_dec, df_record_highs_jan_feb]
        df_record_highs = pd.concat(high_frames)

        df_record_lows_jan_feb = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_lows_dec = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(12-)')]
        low_frames = [df_record_lows_dec, df_record_lows_jan_feb]
        df_record_lows = pd.concat(low_frames)

        df_high_norms_jan_feb = df_norms[3][0:60]
        df_high_norms_dec = df_norms[3][335:]
        high_norm_frames = [df_high_norms_dec, df_high_norms_jan_feb]
        df_high_norms = pd.concat(high_norm_frames)

        df_low_norms_jan_feb = df_norms[4][0:60]
        df_low_norms_dec = df_norms[4][335:]
        low_norm_frames = [df_low_norms_dec, df_low_norms_jan_feb]
        df_low_norms = pd.concat(low_norm_frames)

        bar_x = date_time
        nh_value = df_high_norms
        nl_value = df_low_norms
        rh_value = df_record_highs[0]
        rl_value = df_record_lows[0]

    else:
        temps = temps_cy
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    mkr_color = {'color':'black'}
      
    trace = [
            go.Bar(
                y = temps['dif'],
                x = bar_x,
                base = temps['TMIN'],
                name='Temp Range',
                marker = mkr_color,
                hovertemplate = 'Temp Range: %{y} - %{base}<extra></extra><br>'
                                # 'Record High: %{temps[6]}'                  
            ),
            go.Scatter(
                y = nh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal High',
                marker = {'color':'indianred'}
            ),
            go.Scatter(
                y = nl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal Low',
                marker = {'color':'slateblue'}
            ),
            go.Scatter(
                y = rh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record High',
                marker = {'color':'red'}
            ),
            go.Scatter(
                y = rl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record Low',
                marker = {'color':'blue'}
            ),
        ]
    layout = go.Layout(
                xaxis = {'rangeslider': {'visible':False},},
                yaxis = {"title": 'Temperature F'},
                title ='Daily Temps',
                plot_bgcolor = 'lightgray',
                height = 500,
        )
    return {'data': trace, 'layout': layout}, temps.to_json()

@app.callback(
    Output('graph', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')
    elif value == 'fyma-graph':
        return dcc.Graph(id='fyma-graph')
    elif value == 'frbg':
        return dcc.Graph(id='frs-bar')
    elif value == 'frhm':
        return dcc.Graph(id='frs-heat')

@app.callback(
    Output('params', 'children'),
    [Input('product', 'value')])
def display_param_row(product_value):
    if product_value == 'temp-graph':
        return html.Div([
            html.Div([
                html.P('Enter Year (YYYY):'),
            ],
                className='two columns'
            ),
            dcc.Input(
                id = 'year',
                type = 'number',
                value = str(current_year),
                min = 1950, 
                max = current_year
            ),
            dcc.RadioItems(
                    id = 'period',
                    options = [
                        {'label':'Annual (Jan-Dec)', 'value':'annual'},
                        {'label':'Winter (Dec-Feb)', 'value':'winter'},
                        {'label':'Spring (Mar-May)', 'value':'spring'},
                        {'label':'Summer (Jun-Aug)', 'value':'summer'},
                        {'label':'Fall (Sep-Nov)', 'value':'fall'},
                    ],
                    # value = 'annual',
                    labelStyle = {'display':'inline'}
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
    elif product_value == 'climate-for-day':
        return html.Div([
            html.Div([
                dcc.RadioItems(
                    id = 'temp-param',
                    options = [
                        {'label':'Max Temp', 'value':'TMAX'},
                        {'label':'Min Temp', 'value':'TMIN'},
                        {'label':'Temp Range', 'value':'RANGE'},
                    ],
                    # value = 'TMAX',
                    labelStyle = {'display':'inline-block'}
                ),
            ],
                className='four columns'
            ),
            html.Div([
                html.P('Select Date (MM-DD):'),
            ],
                className='two columns'
            ),
            html.Div([
                dcc.DatePickerSingle(
                    id='date',
                    display_format='MM-DD',
                    date=today
                )
            ]),
        ],
            className='row'
        ),

@app.callback(Output('all-data', 'children'),
            [Input('product', 'value')])
def all_temps_cleaner(product_value):
  
    cleaned_all_temps = df_all_temps
    cleaned_all_temps.columns=['dow','sta','Date','TMAX','TMIN']
    # cleaned_all_temps['Date'] = pd.to_datetime(cleaned_all_temps['Date'])
    cleaned_all_temps = cleaned_all_temps.drop(['dow','sta'], axis=1)

    return cleaned_all_temps.to_json()

@app.callback(Output('rec-highs', 'children'),
             [Input('year', 'value')])
def rec_high_temps(selected_year):
    if int(selected_year) % 4 == 0:
        rec_highs = df_rec_highs
    else:
        rec_highs = df_rec_highs.drop(df_rec_highs.index[59])
    return rec_highs.to_json()

@app.callback(Output('rec-lows', 'children'),
             [Input('year', 'value')])
def rec_low_temps(selected_year):
    if int(selected_year) % 4 == 0:
        rec_lows = df_rec_lows
    else:
        rec_lows = df_rec_lows.drop(df_rec_lows.index[59])
    return rec_lows.to_json()

@app.callback(Output('norms', 'children'),
             [Input('product', 'value')])
def norm_highs(product):
    norms = df_norms
    return norms.to_json()

@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
    previous_year = int(selected_year) - 1
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")
        cursor = connection.cursor()

        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) IN ({},{}) ORDER BY "DATE" ASC'.format(selected_year, previous_year)
        # postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE
        cursor.execute(postgreSQL_select_year_Query)
        temp_records = cursor.fetchall()
        df = pd.DataFrame(temp_records)
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return df.to_json()

if __name__ == "__main__":
    app.run_server(port=8025, debug=False)
