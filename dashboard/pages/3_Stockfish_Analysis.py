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
    game_id = st.text_input("Enter game ID (for Stockfish Analysis):")


#########################################################
# Display aggregate metrics for Stockfish analysis
#########################################################

st.title(f"Stockfish Analysis")

col1, col2, col3, col4 = st.columns(4)
number_of_games_analyzed = count_number_of_games_analyzed(collection, None, None, None, None, None, game_id)
col1.metric(label="Games Analyzed by Stockfish", value=number_of_games_analyzed)

number_of_blunders = count_number_of_blunders(collection, None, None, None, None, None, game_id)
col2.metric(label="Number of Blunders", value=number_of_blunders)

number_of_inaccuracies = count_number_of_inaccuracies(collection, None, None, None, None, None, game_id)
col3.metric(label="Number of Inaccuracies", value=number_of_inaccuracies)

number_of_mistakes = count_number_of_mistakes(collection, None, None, None, None, None, game_id)
col4.metric(label="Number of Mistakes", value=number_of_mistakes)


# Create the chart for player's expectation for single game
if game_id:
    game = collection.find_one({"_id": game_id})

    if not game.get('player_expectation'):
        st.warning(f"Player expectation data not available for game_id: {game_id}. Trigger the analysis DAG in Airflow")
        st.stop()
    
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
else:
    st.subheader("Please enter a game ID to analyze.")

