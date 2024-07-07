import streamlit as st
from queries import *
import datetime
from dateutil.relativedelta import relativedelta


player = 'hikaru'

# Connect to MongoDB
client, db, collection = connect_to_mongo()

st.title(f"Chess Stats for {player}")

with st.sidebar:
    player_name = st.text_input("Enter player name:")

print('\n\n\n\n')
all_games = get_all_games(collection, player)
all_games_as_white = get_all_games_as_white(collection, player)
all_games_as_black = get_all_games_as_black(collection, player)

current_month = datetime.datetime.now().strftime('%Y_%m')
last_month = (datetime.datetime.now() - relativedelta(months=1)).strftime('%Y_%m')

all_games_played_this_month = get_all_games_played_in_a_month(collection, player, current_month)
all_games_played_last_month = get_all_games_played_in_a_month(collection, player, last_month)

# test3 = get_games_this_month(collection)
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Games Played", value=all_games)
col2.metric(label="Games Played as White", value=all_games_as_white)
col3.metric(label="Games Played as Black", value=all_games_as_black)
col4.metric(label="Games Played This Month", value=all_games_played_this_month, delta=all_games_played_this_month-all_games_played_last_month)





# # games = collection.find(1)  # Fetch all games (customize your query as needed)