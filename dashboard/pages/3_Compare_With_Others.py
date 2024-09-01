import streamlit as st
from queries import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from collections import defaultdict


# Connect to MongoDB
client, db, collection = connect_to_mongo()

with st.sidebar:
    player = st.text_input("Enter player username:")
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "rapid", "daily"])
    color = st.radio("Color", ["All","White", "Black"]).lower()
    date = st.date_input('Start Date', value=None, min_value=datetime(2005,1,1))

# player = 'hikaru'
# print('\n\n\n\n')

if not player:
    st.error("Please enter a player username")
    st.stop()
else:
    player = player.lower() # make it case-insensitive because the data is stored in lowercase

if time_class == "All":
    time_class = None

if color == "all":
    color = None

if not collection.find_one({"player": player}):
    st.error("No user data for selected player. Enter a valid player username.")
    st.stop()

if date:
    date = datetime.combine(date, datetime.min.time()).timestamp() # cast date to datetime and convert to epoch time
    latest_end_time_for_player = collection.find({"player": player}).sort({"end_time": -1}).limit(1)
    latest_end_time_value = latest_end_time_for_player[0]["end_time"]
    if date > latest_end_time_value:
        st.error(f"No data for selected date range. Enter an earlier date. The latest date with game data for {player} is {datetime.fromtimestamp(latest_end_time_value).strftime('%Y-%m-%d')}.")
        st.stop()



#########################################################
# Query Mongo and collect all the data
#########################################################

#########################################################
# Create and save charts as figures
#########################################################

#########################################################
# Assemble Dashboard
#########################################################
st.title("Compare Your Performance Against Others")