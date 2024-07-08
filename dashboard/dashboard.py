import streamlit as st
from queries import *
import datetime
from dateutil.relativedelta import relativedelta

import plotly.express as px
import plotly.graph_objects as go


# Connect to MongoDB
client, db, collection = connect_to_mongo()

with st.sidebar:
    player = st.text_input("Enter player username:")
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "daily"]) # TODO: Eventually make it a multiselect (different data structure than single select): https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
    color = st.radio("Color", ["All","White", "Black"]).lower()

player = 'hikaru' # TODO: remove. This is just for testing
print('\n\n\n\n')

if not player:
    st.error("Please enter a player username")
    st.stop()

if time_class == "All":
    time_class = None

if color == "all":
    color = None

st.title(f"Chess Stats for {player}")

all_games = get_all_games(collection, player, time_class, color)
all_games_as_white = get_all_games_as_white(collection, player, time_class, color)
all_games_as_black = get_all_games_as_black(collection, player, time_class, color)

current_month = datetime.datetime.now().strftime('%Y_%m')
last_month = (datetime.datetime.now() - relativedelta(months=1)).strftime('%Y_%m')

all_games_played_this_month = get_all_games_played_in_a_month(collection, player, current_month, time_class, color)
all_games_played_last_month = get_all_games_played_in_a_month(collection, player, last_month, time_class, color)

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Games Played", value=all_games)
col2.metric(label="Games Played as White", value=all_games_as_white)
col3.metric(label="Games Played as Black", value=all_games_as_black)
col4.metric(label="Games Played This Month", value=all_games_played_this_month, delta=all_games_played_this_month-all_games_played_last_month)

col1, col2, col3 = st.columns(3)

results_as_white = get_win_loss_counts(collection, player, 'white', time_class, color)
labels_white = ['lose' if doc['_id'] in('resigned','checkmated','timeout','abandoned') 
          else "draw" if doc["_id"] in ('agreed','repetition','insufficient','stalemate') 
          else doc["_id"] for doc in results_as_white]

values_white = [doc['count'] for doc in results_as_white]

fig = px.pie(
    names=labels_white,
    values=values_white,
    title=f"Game Results as White",
    labels={'names': 'Result', 'values': 'Count'},
    color=labels_white,
    color_discrete_map={
        "win": "#90EE90",
        "lose": "#DD5C5C",
        "draw": "#ADD8E6"
    }
)

col1.plotly_chart(fig)

results_as_white = get_win_loss_counts(collection, player, 'black', time_class, color)
labels_black = ['lose' if doc['_id'] in('resigned','checkmated','timeout','abandoned') 
          else "draw" if doc["_id"] in ('agreed','repetition','insufficient','stalemate') 
          else doc["_id"] for doc in results_as_white]

values_black = [doc['count'] for doc in results_as_white]


fig = px.pie(
    names=labels_black,
    values=values_black,
    title=f"Game Results as Black",
    labels={'names': 'Result', 'values': 'Count'},
    color=labels_black,
    color_discrete_map={
        "win": "#90EE90",
        "lose": "#DD5C5C",
        "draw": "#ADD8E6"
    }
)

col2.plotly_chart(fig)

count_time_controls = count_time_controls(collection, player, time_class, color)

labels = [doc["_id"] for doc in count_time_controls]
values = [doc["count"] for doc in count_time_controls]

fig = px.pie(
    names=labels,
    values=values,
    title=f"Summary of Time Controls",
    labels={'names': 'Result', 'values': 'Count'},
)

col3.plotly_chart(fig)


fig = px.bar(
    x=labels_white + labels_black, 
    y=values_white + values_black,
    color=["White"] * len(labels_white) + ["Black"] * len(labels_black),  # Color list
    barmode="group",
    title="Game Results by Color",
    labels={"x": "Result", "y": "Number of Games", "color": "Player Color"}
)

# Display chart
st.plotly_chart(fig)

st.metric(label="Total Games Played", value=50)