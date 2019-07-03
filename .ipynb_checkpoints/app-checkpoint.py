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
          host="130.211.166.226",
          user="pcalderon",
          passwd="pcalderon@mysqlFO",
          database='kayacredit')
    columns = 'msisdn, birthday, gender, city, province, monthly_income, dependents, employment_status, ownership, verified, updated_at'.split(', ')
    query = '''
    select 
        msisdn, birthday, gender, city, province, monthly_income, dependents, employment_status, ownership, verified, updated_at 
    from users
    where date(updated_at) BETWEEN '{}' AND '{}' 
    '''.format(date_min, date_max)
    print(query)
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = pd.DataFrame(mycursor.fetchall())
    myresult.columns = columns
    myresult = myresult[~myresult['msisdn'].isin(msisdns_ayannah)]
    myresult['age'] = datetime.datetime.now().year - pd.to_datetime(myresult['birthday']).dt.year
    myresult['verified'] = myresult['verified'].astype(int).map(fillup)
    myresult['province'] = myresult['province'].str.lower()
    myresult['day'] = pd.to_datetime(myresult['updated_at']).dt.date.map(str)
    print('done loading data')
    return myresult
    
def get_counts(df, column):
    return df.groupby(column).value_counts()
    
###### DASH APPLICATION #######
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'KayaCredit Dashboard'

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label(id = 'label', style={'display': 'inline-block'}),
        ]),
        dcc.DatePickerRange(
            id='dates',
        min_date_allowed=datetime.datetime(2018, 9, 18),
        max_date_allowed=datetime.datetime(2021, 12, 31),
        start_date=datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 1),
        end_date=datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)),
#             min_date_allowed=datetime.datetime(2018, 1, 1),
#             max_date_allowed=datetime.datetime(current_date.year, current_date.month, current_date.day)),
        html.Button('GO', id='button', style={'display': 'inline-block'})
    ]),
    html.Div([
            html.H4(children='Verified'),
            dash_table.DataTable(
                id='verified_dat')
        ], style={'width': '98%', 'display': 'inline-block', 'margin-left': '10px'}),
    html.H1(id='title'),
    html.Div([
        dcc.Graph(id='verified', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
        dcc.Graph(id='age', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='monthly_income', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
        dcc.Graph(id='dependents', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='gender', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
        dcc.Graph(id='province', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='employment_status', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
        dcc.Graph(id='ownership', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'})
    ]),
    html.Div([
            html.H4(children='Num Success'),
            dash_table.DataTable(
                id='success_dat')
        ], style={'width': '98%', 'display': 'inline-block', 'margin-left': '10px'}),
    html.Div(id='raw_data', style={'display': 'none'})
])

@app.callback(
    Output('raw_data', 'children'),
    [Input(component_id='button', component_property='n_clicks')],
    [State('dates', 'start_date'),
     State('dates', 'end_date')])
def load_raw_data(button, start, end):
    overall = get_data(start, end)
    return overall.to_json(date_format='iso')
    
### GRAPHING FXNS ###
    
def return_df(data_json, column, filt=None):
    data = pd.read_json(data_json).sort_index()
    if filt is not None:
        data = data[data['verified']=='success']
    to_plot = data[column].value_counts().sort_index(ascending=False).reset_index()
    return to_plot

def graph_pie(data_json, column):
    data = pd.read_json(data_json).sort_index()
    to_plot = data[column].value_counts()
    if column == 'province':
        to_plot = to_plot[to_plot>2]
    x = list(to_plot.index)
    y = list(to_plot.values)
    print(x,y)
    return {
        'data': [go.Pie(labels=x, values=y)],
        'layout': go.Layout(title=column, margin=dict(t=50))}        
    
def graph_hist(data_json, column):
    data = pd.read_json(data_json).sort_index()
    
    if column == 'monthly_income':
        data = data[data[column] < 200000]
    elif column == 'dependents':
        data = data[data[column] < 15]
    to_plot = list(data[column].values)
    
    return {
        'data': [go.Histogram(
            x=list(to_plot)
        )],
        'layout': go.Layout(
            margin=dict(t=50), 
            yaxis=dict(title=column))}       

### PIE CHARTS ###
    
@app.callback(
    Output('verified', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_verified_graph(n_clicks, data_json):
    return graph_pie(data_json, 'verified')
    
@app.callback(
    Output('gender', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_gender_graph(n_clicks, data_json):
    return graph_pie(data_json, 'gender')
    
@app.callback(
    Output('province', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_province_graph(n_clicks, data_json):
    return graph_pie(data_json, 'province')
    
@app.callback(
    Output('employment_status', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_employment_status_graph(n_clicks, data_json):
    return graph_pie(data_json, 'employment_status')
    
@app.callback(
    Output('ownership', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_ownership_graph(n_clicks, data_json):
    return graph_pie(data_json, 'ownership')
    
### HISTOGRAMS ###
    
@app.callback(
    Output('age', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_age_graph(n_clicks, data_json):
    return graph_hist(data_json, 'age')

@app.callback(
    Output('monthly_income', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_monthly_income_graph(n_clicks, data_json):
    return graph_hist(data_json, 'monthly_income')

@app.callback(
    Output('dependents', 'figure'),
    [Input(component_id='button', component_property='n_clicks'),
     Input('raw_data', 'children')],
)
def update_dependents_graph(n_clicks, data_json):
    return graph_hist(data_json, 'dependents')
    
@app.callback(
    Output('verified_dat', 'columns'),
    [Input('raw_data', 'children')])
def update_customers_columns(data_json):
    df = return_df(data_json, 'verified')
    return [{"name": i, "id": i} for i in df.columns]

@app.callback(
    Output('verified_dat', 'data'),
    [Input('raw_data', 'children')])
def update_customers_data(data_json):
    df = return_df(data_json, 'verified')
    return df.to_dict("rows")

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


@app.callback(
    Output('label', 'children'),
    [Input('button', 'n_clicks')])
def update_label(n_clicks):
    return 'Please select year. (Updated: {})'.format(str(datetime.datetime.now() + datetime.timedelta(hours=8)))

if __name__ == '__main__':
    app.run_server(debug=True, port=8057,host='0.0.0.0')