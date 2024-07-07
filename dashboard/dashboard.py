import streamlit as st
from queries import *


st.title('Chess Analytics Dashboard')

# # # Connect to MongoDB
# # client, db, collection = connect_to_mongo()

# # Title

# with st.sidebar:
#     player_name = st.text_input("Enter player name:")

test = get_all_games() 
test2 = get_half_games() 


st.metric(label="Total Games Played", value=test, delta=15)
st.metric(label="Total Games Played", value=test*32, delta=15)
st.metric(label="Total Games Played", value=test*32, delta=15)




# # games = collection.find(1)  # Fetch all games (customize your query as needed)