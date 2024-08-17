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
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "rapid", "daily"]) 
    date = st.date_input('Start Date', value=None, min_value=datetime(2005,1,1))

# player = 'hikaru'
# print('\n\n\n\n')

# Don't want an `if not player` error like on the other dashboard. Should be able to browse all games.
if player:
    player = player.lower()

if time_class == "All":
    time_class = None

if not player:
    pass
elif not collection.find_one({"player": player}):
    st.error("No user data for selected player. Enter a valid player username.")
    st.stop()


#########################################################
# Query Mongo and collect all the data
#########################################################

games = display_100_games(collection, player, time_class, date)
# pprint(collection.find_one({'player': player})) # TODO: delete this

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

    start_time = game.get('start_time')
    if start_time:
        row_data['Start Date'] = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
    else:
        row_data['Start Date'] = 'N/A'

    table_data.append(row_data)

df = pd.DataFrame(table_data)

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

