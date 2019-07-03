import pandas as pd
import mysql.connector
import psycopg2
import matplotlib.pyplot as plt
import os, datetime
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

fillup = {1: 'success',
3: 'incomplete',
4: 'incomplete'}

msisdns_ayannah = ["639054601890","639234432441","639954691207","639198252054","639294994566","639669527604","639669527601","639669527606","639669527602","639669527603","639669527605","639983612928","639434423551","639976691847","639123456789","639170001111","639170001112","639297825756","639178661412"]

def get_data(date_min, date_max):
    mydb = mysql.connector.connect(
      host="192.168.8.11",
      user="chris",
      passwd="password",
      database='kayacredit_chris')
    columns = 'msisdn, birthday, gender, city, province, monthly_income, dependents, employment_status, ownership, verified, updated_at'.split(', ')
    query = '''
    select 
        msisdn, birthday, gender, city, province, monthly_income, dependents, employment_status, ownership, verified, updated_at 
    from users
    where date(updated_at >= CURDATE()) BETWEEN '{}' AND '{}' 
    '''.format(date_min, date_max)
    print(query)
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = pd.DataFrame(mycursor.fetchall())
    myresult.columns = columns
    myresult = myresult[~myresult['msisdn'].isin(msisdns_ayannah)]
    myresult['age'] = datetime.datetime.now().year - pd.to_datetime(myresult['birthday']).dt.year
    myresult['day'] = pd.to_datetime(myresult['updated_at']).dt.date.map(str)
#     myresult['verified'] = myresult['verified'].astype(int).map(fillup)
    print('done loading data')
    return myresult
    
def get_counts(df, column):
    return df.groupby(column).value_counts()
    
def get_index(min_w, min_y, max_w, max_y, month=True):
    if month:
        max_val = 12
    else:
        max_val = 52
    curr_week = min_w
    curr_year = min_y
    dates_collection = []
    while True:
        dates_collection.append(str(curr_year) + '-' + '{:02d}'.format(curr_week))
        curr_week = int(curr_week) + 1
        if curr_week == max_val:
            curr_year = curr_year + 1
            curr_week = 1
            continue
        print(str(curr_year) + '-' + '{:02d}'.format(curr_week))
        if str(curr_year) + '-' + '{:02d}'.format(curr_week) == str(max_y) + '-' + '{:02d}'.format(max_w):
            dates_collection.append(str(curr_year) + '-' + '{:02d}'.format(curr_week))
            print('broke', curr_year, curr_week)
            break
    return dates_collection

month_name_dict = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'May',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Aug',
    '09': 'Sept',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec'
}

def fix_month(x):
    year = x[:4]
    month = x[-2:]
    return month_name_dict[month] + ' ' + year

def fix_week(x):
    year = x[:4]
    week = x[-2:]
    return 'week ' + week + ', ' + year

def get_verified_data(data, index, month=True):
    if month:
        a = pd.Series(data[data['verified']==1].groupby(['year_month']).count()['msisdn'],index=index).fillna(0)
        b = pd.Series(data[data['verified'].isin([3,4])].groupby(['year_month']).count()['msisdn'],index=index).fillna(0)
        
        a = a.sort_index()
        b = b.sort_index()

        a.index = [fix_month(x) for x in list(a.index)]
        b.index = [fix_month(x) for x in list(b.index)]
    else:
        a = pd.Series(data[data['verified']==1].groupby(['year_week']).count()['msisdn'],index=index).fillna(0)
        b = pd.Series(data[data['verified'].isin([3,4])].groupby(['year_week']).count()['msisdn'],index=index).fillna(0)
        
        a = a.sort_index()
        b = b.sort_index()

        a.index = [fix_week(x) for x in list(a.index)]
        b.index = [fix_week(x) for x in list(b.index)]
        
        a = a.tail(20)
        b = b.tail(20)
    return a,b

######DASH APPLICATION #######
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'KayaCredit Dashboard'

app.layout = html.Div([
    html.Label(id='date'),
    html.Button('UPDATE DATA', id='button', style={'display': 'inline-block'}),
    html.H1(id='title'),
    html.Div([
        dcc.Graph(id='verified', style={'width': '100%', 'marginTop': 25, 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='verified_week', style={'width': '100%', 'marginTop': 25, 'display': 'inline-block'}),
    ]),
    html.Div([
            html.H4(children='Num Success'),
            dash_table.DataTable(
                id='success_dat')
        ], style={'width': '98%', 'display': 'inline-block', 'margin-left': '10px'}),
    html.Div(id='raw_data', style={'display': 'none'}),
    html.Div(id='week_data', style={'display': 'none'}),
    html.Div(id='month_data', style={'display': 'none'})
])
    
### GRAPHING FXNS ###

def get_data_by_week_month(week_or_month, data):
    use = data.groupby('year_{}'.format(week_or_month.lower()), 'verified').count()

def graph_bar(a, b, label):
    print(a.index)
    trace1 = go.Bar(
        x=list(a.index),
        y=list(a.values),
        name='complete fillup'
    )
    
    trace2 = go.Bar(
        x=list(b.index),
        y=list(b.values),
        name='not verified'
    )

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(title=label, margin=dict(t=50), barmode='stack')}        

@app.callback(
    Output('raw_data', 'children'),
    [Input(component_id='button', component_property='n_clicks')]
)
def get_week_month_data(n_clicks):
    current_date = datetime.datetime.now()
    data = get_data('2017-01-01', '{}-{}-{}'.format(current_date.year, current_date.month, current_date.day))
    data['month'] = pd.to_datetime(data['updated_at']).dt.month
    data['year'] = pd.to_datetime(data['updated_at']).dt.year
    data['week_number'] = pd.to_datetime(data['updated_at']).dt.strftime("%V").astype(str)
    data['year_month'] = data['year'].astype(str) + '-' + data['month'].map(lambda x: '{:02d}'.format(x))
    data['year_week'] = data['year'].astype(str) + '-' + data['week_number'].astype(str)
    
    return data.to_json(date_format='iso')

def get_week_data(data):
    min_y_yw = int(data['year_week'].min()[:4])
    min_w_yw = int(data['year_week'].min()[-2:])
    max_y_yw = int(data['year_week'].max()[:4])
    max_w_yw = int(data['year_week'].max()[-2:])
    week_index = get_index(min_w_yw, min_y_yw, max_w_yw, max_y_yw, month=False)
    print(min_y_yw, min_w_yw, max_y_yw, max_w_yw)
    print(data)
    print(week_index)
    week_data = get_verified_data(data, week_index, month=False)
    return week_data

def get_month_data(data):
    min_y_ym = int(data['year_month'].min()[:4])
    min_w_ym = int(data['year_month'].min()[-2:])
    max_y_ym = int(data['year_month'].max()[:4])
    max_w_ym = int(data['year_month'].max()[-2:])
    month_index = get_index(min_w_ym, min_y_ym, max_w_ym, max_y_ym, month=True)
    month_data = get_verified_data(data, month_index, month=True)
    return month_data

@app.callback(
    Output('date', 'children'),
    [Input(component_id='button', component_property='n_clicks')]
)
def update_label(n_clicks):
    return 'Click to update graphs. (Updated: {})'.format(str(datetime.datetime.now() + datetime.timedelta(hours=8)))


@app.callback(
    Output('verified', 'figure'),
    [Input(component_id='raw_data', component_property='children')],
)
def update_bar_graph(json_data):
    data = pd.read_json(json_data)
    a, b = get_month_data(data)
    return graph_bar(a, b, 'by Month')

@app.callback(
    Output('verified_week', 'figure'),
    [Input(component_id='raw_data', component_property='children')]
)
def update_bar_graph_week(json_data):
    data = pd.read_json(json_data)
    a, b = get_week_data(data)
    return graph_bar(a, b, 'by Week')

def return_df(data_json, column, filt=None):
    data = pd.read_json(data_json).sort_index()
    if filt is not None:
        data = data[data['verified']==1] 
    print(data)
    to_plot = data[column].value_counts().sort_index(ascending=False).reset_index()
    return to_plot

@app.callback(
    Output('success_dat', 'columns'),
    [Input('raw_data', 'children')])
def update_success_columns(data_json):
    df = return_df(data_json, 'day', filt=1)
    return [{"name": i, "id": i} for i in df.columns]

@app.callback(
    Output('success_dat', 'data'),
    [Input('raw_data', 'children')])
def update_success_data(data_json):
    df = return_df(data_json, 'day', filt=1)
    return df.to_dict("rows")


if __name__ == '__main__':
    app.run_server(debug=True, port=8058, host='0.0.0.0')