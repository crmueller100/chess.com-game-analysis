import streamlit as st
from datetime import datetime
from datetime import timedelta

import pandas as pd
import re
from pprint import pprint

from queries import *

# Connect to MongoDB
client, db, collection = connect_to_mongo()

with st.sidebar:
    player1 = st.text_input("Enter player username:")
    player2 = st.text_input("Enter opponent username:")
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "rapid", "daily"]) 
    date_begin = st.date_input('Date Range Start', value=None, min_value=datetime(2005,1,1))
    date_end = st.date_input('Date Range End', value=None, min_value=datetime(2005,1,1))

# Don't want an `if not player` error like on the other dashboard. Should be able to browse all games.
if player1:
    player1 = player1.lower()

if player2:
    player2 = player2.lower()

if time_class == "All":
    time_class = None

if date_begin:
    date_begin = datetime.combine(date_begin, datetime.min.time()).timestamp() # cast date to datetime and convert to epoch time

if date_end:
    date_end = datetime.combine(date_end, datetime.min.time()) + timedelta(days=1) # Add one day because the date picker defaults to midnight of the selected day
    date_end = date_end.timestamp() 


#########################################################
# Query Mongo and display the data
#########################################################

games = display_100_games(collection, player1, player2, time_class, date_begin, date_end)

table_data = []
keys_to_display = ["_id", "url", "player", "player_expectation", "num_blunders","num_mistakes","num_inaccuracies"]

# Extract values for the specified keys from each game document
for game in games:
    row_data = {key: game.get(key) for key in keys_to_display}

    time_control_str = game.get('time_control')
    match = re.match(r"(\d+)(?:\+(\d+))?", time_control_str)  # Match base time and increment
    
    tc = game.get('time_control')

    if match:
        base_time, increment = match.groups()  # Extract the two parts
        
        if base_time == '30':
            tc = '30 sec bullet'
        elif base_time == '60':
            tc = '1 min bullet'
        elif base_time == '180':
            tc = '3 min blitz'
        elif base_time == '300':
            tc = '5 min blitz'
        elif base_time == '600':
            tc = '10 min rapid'
        elif base_time == '900':
            tc = '15 min rapid'
        elif base_time == '1800':
            tc = '30 min rapid'
        elif tc == '1/259200': # Don't use regex on this game format
            tc = '3 day'
        
        if increment is not None:
            tc += f" +{increment}"  

    row_data['Time control'] = tc
    # row_data['Winner'] = game.get('white', {}).get('username') if game.get('white', {}).get('result') == 'win' else game.get('black', {}).get('username')
    if game.get('white', {}).get('result') == 'win':
        row_data['Winner'] = 'White'
    elif game.get('black', {}).get('result') == 'win':
        row_data['Winner'] = 'Black'
    else:
        row_data['Winner'] = 'draw'

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

st.title(f"Game Explorer")

df = pd.DataFrame(table_data)

if not df.empty:
    # Convert the rating columns to strings to remove commas
    df['White Rating'] = df['White Rating'].astype(str)
    df['Black Rating'] = df['Black Rating'].astype(str)
else:
    st.error("No games found for the specified criteria.")
    st.stop()

st.dataframe(df)


# Display player metadata
games = list(collection.find({}, {'player': 1, 'end_time': 1, 'player_expectation': 1}))

if games:
    df = pd.DataFrame(games)

    # Group by player and calculate the number of games and the most recent game
    player_stats = df.groupby('player').agg(
        number_of_games=('player', 'size'),
        most_recent_game=('end_time', 'max'),
        games_analyzed_by_stockfish=('player_expectation', 'count')
    ).reset_index()

    # Convert the most recent game timestamp to a human-readable date
    player_stats['most_recent_game'] = pd.to_datetime(player_stats['most_recent_game'], unit='s').dt.strftime('%m/%d/%Y')
    
    st.subheader("Player Metadata")
    st.dataframe(player_stats)
else:
    st.error("No games found in the database.")
    st.stop()
