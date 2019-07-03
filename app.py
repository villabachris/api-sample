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
import logging
# import json

log = logging.getLogger(__name__)

fillup = {
            1: 'success',
            3: 'incomplete',
            4: 'incomplete'
        }

msisdns_ayannah = ["639054601890","639234432441","639954691207","639198252054","639294994566","639669527604","639669527601","639669527606","639669527602","639669527603","639669527605","639983612928","639434423551","639976691847","639123456789","639170001111","639170001112","639297825756","639178661412"]

def get_data(date_min, date_max):
    mydb = mysql.connector.connect(
        host="130.211.166.226",
        user="pcalderon",
        passwd="pcalderon@mysqlFO",
        database='kayacredit')
    columns = 'id, msisdn, birthday, gender, city, province, monthly_income, dependents, employment_status, ownership, verified, created_at, updated_at'.split(', ')
    query = '''
    select 
        id, msisdn, birthday, gender, city, province, monthly_income, dependents, employment_status, ownership, verified, created_at,  updated_at 
    from users
    where date(updated_at) BETWEEN '{}' AND '{}' 
    '''.format(date_min, date_max)
    print(query)
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = pd.DataFrame(mycursor.fetchall())
    myresult.columns = columns
    myresult = myresult[~myresult['msisdn'].isin(msisdns_ayannah)]
    myresult['login'] = pd.to_datetime(myresult['created_at']).dt.date.map(str)
    myresult['age'] = datetime.datetime.now().year - pd.to_datetime(myresult['birthday']).dt.year
    myresult['verified'] = myresult['verified'].astype(int).map(fillup)
    myresult['province'] = myresult['province'].str.lower()
    myresult['day'] = pd.to_datetime(myresult['updated_at']).dt.date.map(str)
    print('done loading data')
    return myresult

def get_counts(df, column):
    return df.groupby(column).value_counts()


mydb = mysql.connector.connect(
    # host="192.168.8.11",
    # user="chris",
    # passwd="password",
    # database='kayacredit_chris'
    host="130.211.166.226",
    user="pcalderon",
    passwd="pcalderon@mysqlFO",
    database='kayacredit')
heads = 'id, first_name, verified, proof_billing, proof_income, gov_id'.split(', ')
query = "SELECT id, first_name, verified, proof_billing, proof_income, gov_id FROM users WHERE date(updated_at) = CURDATE()"
mycursor = mydb.cursor()
mycursor.execute(query)
rows = mycursor.fetchall()
# for r in rows:
#     print('first_name = {} last_name = {}'.format(r[0],r[1]))
result = pd.DataFrame(rows)
# not_null = result.notna()
# result.heads = heads
# total_rows = len(result[0])
if result.empty == True:
    print("Wait for Update of "+str(datetime.date.today())+" Data Load...")
else:

    mydb1 = mysql.connector.connect(
        host="130.211.166.226",
        user="pcalderon",
        passwd="pcalderon@mysqlFO",
        database='kayacredit')
    query1 = 'SELECT proof_billing,proof_income,gov_id FROM kayacredit.users WHERE CONCAT(proof_billing,proof_income,gov_id) IS NOT NULL AND date(updated_at) >= CURDATE()'
    cursor1 = mydb1.cursor()
    cursor1.execute(query1)
    rows1 = cursor1.fetchall()
    result1 = pd.DataFrame(rows1)
    total_application = result1[[0]].count().sum()
    print(total_application)


    u_id = result['id'] = result[[0]]
    name = result['first_name'] = result[[1]]
    ver = result['verified'] = result[[2]]
    total_visit = u_id.count().sum()
    success_signups = ver.count().sum()
    total_approvals = ver[ver[2] == '1'].count().sum()

    avg_app = total_application / total_visit * 100  
    avg_sign = success_signups / total_visit  * 100  
    # total_success = name.count().sum()
    #-----
    # total_verified = ver[ver[2] == '3'].count().sum()
    # total_inc = ver[ver[2] == '4'].count().sum()
    # total_signups = total_inc + total_verified
    # total_signups_avg = total_success / total_visit
    # total_app_avg = total_success / total_visit 
    print("Total Count Loading")
    print('total '+str(float(avg_app)))
    print('total '+str(float(avg_sign)))
mydb.close()

# mydb1 = mysql.connector.connect(
#     host="130.211.166.226",
#     user="pcalderon",
#     passwd="pcalderon@mysqlFO",
#     database='kayacredit')
# query1 = 'SELECT proof_billing,proof_income,gov_id FROM kayacredit.users WHERE CONCAT(proof_billing,proof_income,gov_id) IS NOT NULL AND date(updated_at) >= CURDATE()'
# cursor1 = mydb1.cursor()
# cursor1.execute(query1)
# rows1 = cursor1.fetchall()
# result1 = pd.DataFrame(rows1)
# print(result1)


#==============================#
###### DASH APPLICATION #######
#==============================#
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
        start_date=datetime.date.today(),
        end_date=datetime.date.today()),
#             min_date_allowed=datetime.datetime(2018, 1, 1),
#             max_date_allowed=datetime.datetime(current_date.year, current_date.month, current_date.day)),
        html.Button('GO', id='button', style={'display': 'inline-block'})
    ], style={'display':'none'}),
    html.Div([
            html.H4(children='Verified'),
            dash_table.DataTable(
                id='verified_dat')
        ], style={'width': '98%', 'display': 'inline-block', 'margin-left': '10px', 'display':'none'}),
    html.H1(id='title'),
    #===================#
    #total count display
    #==================#
    html.Div([
        html.Div([
            html.Div([
                 html.Div([
                    html.Img(src='/assets/images/globe1.png', style={'width':'65px', 'height':'65px', 'padding-left':'15px'})
                ])
            ],style={'width':'50%', 'height':'100%', 'display':'inline-block'}),
            html.Div([
                html.Div([
                    html.P('No. of Visits to Website'),
                    html.H3(total_visit)
                ])
            ],style={'width':'50%', 'display':'inline-block'}),

            html.Div([
                html.P("Updated As of {}".format(str(datetime.date.today())), style={'text-align':'center'})
            ], style={'border-top':'1px solid#b1b1b1', 'padding':'5px'})
        ], style={'width':'22%','margin':'0 10px', 'display':'inline-block'}),
        
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src='/assets/images/cursor.png', style={'width':'65px', 'height':'65px', 'padding-left':'15px'})
                ])
            ],style={'width':'50%', 'height':'100%', 'display':'inline-block'}),

            html.Div([
                html.Div([
                    html.P('Successful Signups'),
                    html.H3(success_signups)
                ])
            ],style={'width':'50%', 'display':'inline-block'}),

            html.Div([
                html.P("Updated As of {}".format(str(datetime.date.today())), style={'text-align':'center'})
            ], style={'border-top':'1px solid #b1b1b1', 'padding':'5px'})
        ], style={'width':'22%','margin':'0 10px', 'display':'inline-block'}),
        
       
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src='/assets/images/check.png', style={'width':'65px', 'height':'65px', 'padding-left':'15px'})
                ])
            ],style={'width':'50%', 'height':'100%', 'display':'inline-block'}),

            html.Div([
                html.Div([
                    html.P('Successful Applications'),
                    html.H3(total_application)
                ])
            ],style={'width':'50%', 'display':'inline-block'}),

            html.Div([
                html.P("Updated As of {}".format(str(datetime.date.today())), style={'text-align':'center'})
            ], style={'border-top':'1px solid #b1b1b1', 'padding':'5px'})
        ], style={' `width':'22%','margin':'0 10px', 'display':'inline-block'}),
        
        html.Div([
            html.Div([
                 html.Div([
                    html.Img(src='/assets/images/approve.png', style={'width':'65px', 'height':'65px', 'padding-left':'15px'})
                ])
            ],style={'width':'50%', 'height':'100%', 'display':'inline-block'}),

            html.Div([
                html.Div([
                    html.P('No. of Approvals',style={'line-height':'317%'}),
                    html.H3(total_approvals)
                ])
            ],style={'width':'50%', 'display':'inline-block'}),

            html.Div([
                html.P("Updated As of {}".format(str(datetime.date.today())), style={'text-align':'center'}),
            ], style={'border-top':'1px solid #b1b1b1', 'padding':'5px'})
        ], style={'width':'22%','margin':'0 10px', 'display':'inline-block'}),
    ], style={'width':'80%', 'margin':'50px auto 100px'}),

    #===============#
    #Conversion
    #===============#
    html.Div([
         html.Div([
            html.Div([
                 html.Div([
                    html.Img(src='/assets/images/convert1.png', style={'width':'65px', 'height':'65px', 'padding-left':'15px'})
                ])
            ],style={'width':'50%', 'height':'100%', 'display':'inline-block'}),
            html.Div([
                html.Div([
                    html.P('Application Conversion'),
                    html.H3(str(float(round(avg_app, 2)))+"%")
                ])
            ],style={'width':'50%', 'display':'inline-block'}),

            html.Div([
                html.P("Updated As of {}".format(str(datetime.date.today())), style={'text-align':'center'})
            ], style={'border-top':'1px solid #b1b1b1', 'padding':'5px'})
        ], style={'width':'22%','margin':'0 10px', 'display':'inline-block'}),

        html.Div([
            html.Div([
                 html.Div([
                    html.Img(src='/assets/images/convert2.png', style={'width':'65px', 'height':'65px', 'padding-left':'15px'})
                ])
            ],style={'width':'50%', 'height':'100%', 'display':'inline-block'}),
            html.Div([
                html.Div([
                    html.P('Signup Coversion', style={'line-height':'317%'}),
                    html.H3(str(float(avg_sign))+"%")
                ])
            ],style={'width':'50%', 'display':'inline-block'}),

            html.Div([
                html.P("Updated As of {}".format(str(datetime.date.today())), style={'text-align':'center'})
            ], style={'border-top':'1px solid #b1b1b1', 'padding':'5px'})
        ], style={'width':'22%','margin':'0 10px', 'display':'inline-block'}),
    ], style={'width':'80%', 'margin':'30px auto 100px'}),
           
    ####################
    #--total count display
    ####################
    
    html.Div([
        dcc.Graph(id='employment_status', style={'width': '35%', 'marginTop': 25, 'display': 'inline-block'}),
        dcc.Graph(id='gender', style={'width': '30%', 'marginTop': 25, 'display': 'inline-block'}),
        dcc.Graph(id='province', style={'width': '30%', 'marginTop': 25, 'display': 'inline-block'}),
        dash_table.DataTable(id='total_verified'),
        html.Div([html.P("Updated As of {}".format(str(str(datetime.datetime.now()))), style={ 'text-align':'center', 'border': '1px solid #b1b1b1'})],style={ 'width':'100%'})
    ], style={'margin-left':'5%', 'marginTop': 0}),
    html.Div([
        dcc.Graph(id='ownership', style={'width': '50%', 'marginTop': 10, 'display': 'inline-block'}),
        dcc.Graph(id='verified', style={'width': '50%', 'marginTop': 25, 'display': 'inline-block'}),
        html.Div([html.P("Updated As of {}".format(str(str(datetime.datetime.now()))), style={ 'text-align':'center', 'border': '1px solid #b1b1b1'})],style={ 'width':'100%'}),
        dcc.Graph(id='monthly_income', style={'width': '100%', 'marginTop': 25, 'display': 'block'}),
        html.Div([html.P("Updated As of {}".format(str(str(datetime.datetime.now()))), style={ 'text-align':'center', 'border': '1px solid #b1b1b1'})],style={ 'width':'100%'}),
        
        
        dcc.Graph(id='dependents', style={'width': '100%', 'marginTop': 25, 'display': 'block'}),
        html.Div([html.P("Updated As of {}".format(str(str(datetime.datetime.now()))), style={ 'text-align':'center', 'border': '1px solid #b1b1b1'})],style={ 'width':'100%'}),
    ], style={'width':'50%', 'margin': '0 auto'}),
    
    html.Div([
        html.Div(dcc.Graph(id='age', style={'width': '100%', 'display': 'inline-block'})),
    ], style={'width':'50%', 'margin':'0 auto'}),
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
            x=list(to_plot),
                
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