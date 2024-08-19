import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import strftime, localtime

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from collections import defaultdict
from pprint import pprint

import pandas as pd
import numpy as np

from queries import *

# Connect to MongoDB
client, db, collection = connect_to_mongo()

with st.sidebar:
    player = st.text_input("Enter player username:")
    player2 = st.text_input("Enter opponent username:")
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "rapid", "daily"]) 
    date = st.date_input('End Date', value=None, min_value=datetime(2005,1,1))

# player = 'hikaru'
# print('\n\n\n\n')

# Don't want an `if not player` error like on the other dashboard. Should be able to browse all games.
if player:
    player = player.lower()

if player2:
    player2 = player2.lower()

if time_class == "All":
    time_class = None

if date:
    date = datetime.combine(date, datetime.min.time()).timestamp() # cast date to datetime and convert to epoch time

#########################################################
# Query Mongo and collect all the data
#########################################################

games = display_100_games(collection, player, player2, time_class, date)

keys_to_display = ["_id", "url"]

table_data = []

# Extract values for the specified keys from each game document
for game in games:
    row_data = {key: game.get(key) for key in keys_to_display}
    tc = game.get('time_control')
    if game.get('time_control') == '30':
        tc = '30 sec bullet'
    elif game.get('time_control') == '60':
        tc = '1 min bullet'
    elif game.get('time_control') == '180':
        tc = '3 min blitz'
    elif game.get('time_control') == '300':
        tc = '5 min blitz'
    elif game.get('time_control') == '600':
        tc = '10 min rapid'
    elif game.get('time_control') == '900':
        tc = '15 min rapid'
    elif game.get('time_control') == '1800':
        tc = '30 min rapid'
    elif game.get('time_control') == '1/259200':
        tc = '3 day'

    row_data['Time control'] = tc
    row_data['Winner'] = game.get('white', {}).get('username') if game.get('white', {}).get('result') == 'win' else game.get('black', {}).get('username')
    row_data['White'] = game.get('white', {}).get('username')
    row_data['White Rating'] = game.get('white', {}).get('rating')
    row_data['Black'] = game.get('black', {}).get('username')
    row_data['Black Rating'] = game.get('black', {}).get('rating')

    end_time = game.get('end_time')
    if end_time:
        row_data['End Date'] = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
    else:
        row_data['End Date'] = 'N/A'

    table_data.append(row_data)


df = pd.DataFrame(table_data)

if not df.empty:
    # Convert the rating columns to strings to remove commas
    df['White Rating'] = df['White Rating'].astype(str)
    df['Black Rating'] = df['Black Rating'].astype(str)

st.dataframe(df)


#########################################################
# Create and save charts as figures
#########################################################


#########################################################
# Assemble Dashboard
#########################################################

st.title(f"Stockfish Analysis for {player}")

