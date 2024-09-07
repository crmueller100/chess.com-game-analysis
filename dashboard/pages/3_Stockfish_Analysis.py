import streamlit as st
from datetime import datetime
from datetime import timedelta

import pandas as pd
import re
from pprint import pprint

import plotly.graph_objects as go

from queries import *

# Connect to MongoDB
client, db, collection = connect_to_mongo()

with st.sidebar:
    player1 = st.text_input("Enter player username:")
    player2 = st.text_input("Enter opponent username:")
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "rapid", "daily"]) 
    date_begin = st.date_input('Date Range Start', value=None, min_value=datetime(2005,1,1))
    date_end = st.date_input('Date Range End', value=None, min_value=datetime(2005,1,1))
    game_id = st.text_input("Enter game ID (for Stockfish Analysis):")

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
# Query Mongo and collect all the data
#########################################################


st.title(f"Stockfish Analysis")

col1, col2, col3, col4 = st.columns(4)
number_of_games_analyzed = count_number_of_games_analyzed(collection, player1, player2, time_class, date_begin, date_end, game_id)
col1.metric(label="Games Analyzed by Stockfish", value=number_of_games_analyzed)

number_of_blunders = count_number_of_blunders(collection, player1, player2, time_class, date_begin, date_end, game_id)
col2.metric(label="Number of Blunders", value=number_of_blunders)

number_of_inaccuracies = count_number_of_inaccuracies(collection, player1, player2, time_class, date_begin, date_end, game_id)
col3.metric(label="Number of Inaccuracies", value=number_of_inaccuracies)

number_of_mistakes = count_number_of_mistakes(collection, player1, player2, time_class, date_begin, date_end, game_id)
col4.metric(label="Number of Mistakes", value=number_of_mistakes)

# TODO: Fix these next 2 lines
game_id = '2347dba8-6a59-11ef-a6d9-6cfe544c0428'
if game_id:
    
    game = collection.find_one({"_id": game_id})
    
    st.header(f"Running analysis for game_id: {game_id}")
    player_expectation = game['player_expectation']
    move_numbers = list(range(1, len(player_expectation) + 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=move_numbers, y=player_expectation, mode='lines+markers', name='Player Expectation'))

    fig.update_layout(
        xaxis_title='Move Number',
        yaxis_title='Win/Loss/Draw Expectation',
        title='Player Expectation Over Time',
    )

    st.plotly_chart(fig)



#########################################################
# Create and save charts as figures
#########################################################


#########################################################
# Assemble Dashboard
#########################################################


