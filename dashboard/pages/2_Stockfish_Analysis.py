import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from collections import defaultdict

from queries import *


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



#########################################################
# Query Mongo and collect all the data
#########################################################



#########################################################
# Create and save charts as figures
#########################################################



#########################################################
# Assemble Dashboard
#########################################################
st.title(f"Stockfish Analysis for {player}")

