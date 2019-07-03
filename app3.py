import pandas as pd
import numpy as np
import mysql.connector
import psycopg2
# import matplotlib.pyplot as plt
import os, datetime
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import logging
import json

mydb = mysql.connector.connect(
    host="192.168.8.11",
    user="chris",
    passwd="password",
    database='kayacredit_chris')
query = "SELECT COUNT(*) FROM users WHERE verified >= 1"
mycursor = mydb.cursor()
mycursor.execute(query)
rows = mycursor.fetchall()
# for r in rows:
#     print('first_name = {} last_name = {}'.format(r[0],r[1]))
result = pd.DataFrame(rows)
print(result.to_json())
mydb.close()