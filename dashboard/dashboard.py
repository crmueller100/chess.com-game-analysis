import streamlit as st
from queries import *
import datetime
from dateutil.relativedelta import relativedelta

import plotly.express as px
import plotly.graph_objects as go

from collections import defaultdict


# Connect to MongoDB
client, db, collection = connect_to_mongo()

with st.sidebar:
    player = st.text_input("Enter player username:")
    time_class = st.selectbox("Time Control", ["All","bullet", "blitz", "daily"]) # TODO: Eventually make it a multiselect (different data structure than single select): https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
    color = st.radio("Color", ["All","White", "Black"]).lower()

# player = 'hikaru' # TODO: remove. This is just for testing
print('\n\n\n\n')

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
    st.error("Ain't no player by that there name. Enter a valid player username.")
    st.stop()


#########################################################
# Query Mongo and collect all the data
#########################################################

current_month = datetime.datetime.now().strftime('%Y_%m')
last_month = (datetime.datetime.now() - relativedelta(months=1)).strftime('%Y_%m')

all_games = get_all_games(collection, player, time_class, color)
all_games_as_white = get_all_games_as_white(collection, player, time_class, color)
all_games_as_black = get_all_games_as_black(collection, player, time_class, color)

all_games_played_this_month = get_all_games_played_in_a_month(collection, player, current_month, time_class, color)
all_games_played_last_month = get_all_games_played_in_a_month(collection, player, last_month, time_class, color)

results_as_white = get_win_loss_counts(collection, player, 'white', time_class, color)
results_as_black = get_win_loss_counts(collection, player, 'black', time_class, color)

count_time_controls = count_time_controls(collection, player, time_class, color)
count_detailed_time_controls = count_detailed_time_controls(collection, player, time_class, color)

rating_of_time_controls_over_time = rating_of_time_controls_over_time(collection, player, time_class, color)


#########################################################
# Create and save charts as figures
#########################################################

raw_labels_white = [doc["_id"] for doc in results_as_white]
casted_labels_white = ['lose' if doc['_id'] in('resigned','checkmated','timeout','abandoned') 
          else "draw" if doc["_id"] in ('agreed','repetition','insufficient','stalemate') 
          else doc["_id"] for doc in results_as_white]

values_white = [doc['count'] for doc in results_as_white]

game_results_as_white = px.pie(
    names=raw_labels_white,
    values=values_white,
    title=f"Game Results as White",
    labels={'names': 'Result', 'values': 'Count'},
    color=raw_labels_white,
    color_discrete_map={
        "win": "#90EE90",
        "lose": "#DD5C5C",
        "draw": "#ADD8E6"
    }
)

raw_labels_black = [doc["_id"] for doc in results_as_black]

casted_labels_black = ['lose' if doc['_id'] in('resigned','checkmated','timeout','abandoned') 
          else "draw" if doc["_id"] in ('agreed','repetition','insufficient','stalemate') 
          else doc["_id"] for doc in results_as_black]

values_black = [doc['count'] for doc in results_as_black]

game_results_as_black = px.pie(
    names=raw_labels_black,
    values=values_black,
    title=f"Game Results as Black",
    labels={'names': 'Result', 'values': 'Count'},
    color=raw_labels_black,
    color_discrete_map={
        "win": "#90EE90",
        "lose": "#DD5C5C",
        "draw": "#ADD8E6"
    }
)

labels = [doc["_id"] for doc in count_time_controls]
values = [doc["count"] for doc in count_time_controls]

summary_of_time_controls = px.pie(
    names=labels,
    values=values,
    title=f"Summary of Time Controls",
    labels={'names': 'Result', 'values': 'Count'},
)

# Need to aggregate the labels because we casted unique labels to categories (e.g. stalemate -> draw)
def aggregate_values(labels, values):
    aggregated = defaultdict(int)
    for label, value in zip(labels, values):
        aggregated[label] += value
    return list(aggregated.keys()), list(aggregated.values())

labels_white, values_white = aggregate_values(casted_labels_white, values_white)
labels_black, values_black = aggregate_values(casted_labels_black, values_black)

total_white = sum(values_white)
total_black = sum(values_black)

percentages_white = [(value / total_white) * 100 for value in values_white]
percentages_black = [(value / total_black) * 100 for value in values_black]

bar_chart_of_win_draw_loss_percentage = px.bar(
    x=labels_white + labels_black, 
    y=percentages_white + percentages_black,
    color=["White"] * len(labels_white) + ["Black"] * len(labels_black),
    barmode="group",
    title="Game Results by Color",
    labels={"x": "Result", "y": "Percentage of Games (%)", "color": "Player Color"},
    category_orders={"x": ["win", "draw", "lose"]},
    text=percentages_white + percentages_black
)

bar_chart_of_win_draw_loss_percentage.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

detailed_time_control_labels = [doc["_id"] for doc in count_detailed_time_controls]
detailed_time_control_values = [doc["count"] for doc in count_detailed_time_controls]

detailed_time_control_chart = px.pie(
    names=detailed_time_control_labels,
    values=detailed_time_control_values,
    title='Time Control Breakdown',
    labels={'names': 'Result', 'values': 'Count'}
    )

average_rating_over_time = [round(doc["avg_rating"],1) for doc in rating_of_time_controls_over_time]
average_rating_over_time_dates = [doc["date"] for doc in rating_of_time_controls_over_time]
average_rating_over_time_class = [doc["time_class"] for doc in rating_of_time_controls_over_time]
average_rating_over_time_class_counts = [doc["count"] for doc in rating_of_time_controls_over_time]

# Create a line chart with Plotly
ratings_over_time_by_time_class = px.line(
    x=average_rating_over_time_dates,
    y=average_rating_over_time,
    color=average_rating_over_time_class,
    labels={'x': 'Date', 'y': 'Average Rating', 'color': 'Time Class'},
    title='Average Rating Over Time by Time Class',
    hover_data={'# Games': average_rating_over_time_class_counts},
    markers=True
)

# Customize the layout
ratings_over_time_by_time_class.update_layout(
    xaxis_title='Date',
    yaxis_title='Average Rating',
    legend_title='Time Class'
)


# #########################################################
# # Assemble Dashboard
# #########################################################
st.title(f"Chess Stats for {player}")

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Games Played", value=all_games)
col2.metric(label="Games Played as White", value=all_games_as_white)
col3.metric(label="Games Played as Black", value=all_games_as_black)
col4.metric(label="Games Played This Month", value=all_games_played_this_month, delta=all_games_played_this_month-all_games_played_last_month)

col1, col2 = st.columns([2,1])

col1.plotly_chart(bar_chart_of_win_draw_loss_percentage)  
col2.plotly_chart(summary_of_time_controls) 

st.subheader("Game Details")

col1, col2, col3 = st.columns(3)

col1.plotly_chart(game_results_as_white)
col2.plotly_chart(game_results_as_black)
col3.plotly_chart(detailed_time_control_chart)

st.plotly_chart(ratings_over_time_by_time_class)

# st.subheader("TODO: Maybe add a heatmap of ways of results of wins vs results of losses?")
# # st.metric(label="Total Games Played", value=50)

