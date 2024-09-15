import streamlit as st
from datetime import datetime
import time
from time import strftime
from dateutil.relativedelta import relativedelta
import pandas as pd

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

current_month = datetime.now().strftime('%Y_%m')
last_month = (datetime.now() - relativedelta(months=1)).strftime('%Y_%m')

latest_game_data = strftime('%m/%d/%y', time.gmtime(get_latest_game(collection, player)['end_time']))

all_games = get_all_games(collection, player, time_class, color, date)
all_games_as_white = get_all_games_as_white(collection, player, time_class, color, date)
all_games_as_black = get_all_games_as_black(collection, player, time_class, color, date)

all_games_played_this_month = get_all_games_played_in_a_month(collection, player, current_month, time_class, color, date)
all_games_played_last_month = get_all_games_played_in_a_month(collection, player, last_month, time_class, color, date)

results_as_white = get_win_loss_counts(collection, player, 'white', time_class, color, date)
results_as_black = get_win_loss_counts(collection, player, 'black', time_class, color, date)

count_time_controls = count_time_controls(collection, player, time_class, color, date)
count_detailed_time_controls = count_detailed_time_controls(collection, player, time_class, color, date)

rating_of_time_controls_over_time = rating_of_time_controls_over_time(collection, player, time_class, color, date)

# TODO: Make the "eco_opening" argument a filter and change between "eco_opening" and "eco_opening_general"
summary_of_all_eco_openings = summary_of_all_eco_openings(collection, player, time_class, color, date, "eco_opening")

#########################################################
# Create and save charts as figures
#########################################################

raw_labels_white = [doc["_id"] for doc in results_as_white]
casted_labels_white = ['lose' if doc['_id'] in('resigned','checkmated','timeout','abandoned') 
          else "draw" if doc["_id"] in ('agreed','repetition','insufficient','stalemate','timevsinsufficient') 
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
          else "draw" if doc["_id"] in ('agreed','repetition','insufficient','stalemate','timevsinsufficient') 
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

# Create time class line chart with bars of games played below
ratings_over_time_by_time_class = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    subplot_titles=('Average Rating per Day', 'Number of Games Played'),
    vertical_spacing=0.1,
    row_heights=[0.75, 0.25]  # Make the line chart row larger
)

# Line chart for average rating over time
for time_class in set(average_rating_over_time_class):
    mask = [tc == time_class for tc in average_rating_over_time_class]
    ratings_over_time_by_time_class.add_trace(
        go.Scatter(
            x=[d for d, m in zip(average_rating_over_time_dates, mask) if m],
            y=[round(r, 1) for r, m in zip(average_rating_over_time, mask) if m],
            mode='lines+markers',
            name=time_class
        ),
        row=1, col=1
    )

# Bar chart for number of games played
ratings_over_time_by_time_class.add_trace(
    go.Bar(
        x=average_rating_over_time_dates,
        y=average_rating_over_time_class_counts,
        name='# Games Played'
    ),
    row=2, col=1
)

ratings_over_time_by_time_class.update_layout(
    height=600,
    title_text='Ratings Over Time For Each Time Class',
)

ratings_over_time_by_time_class.update_xaxes(title_text='Date', row=2, col=1)
ratings_over_time_by_time_class.update_yaxes(title_text='Average Rating', row=1, col=1)
ratings_over_time_by_time_class.update_yaxes(title_text='Number of Games', row=2, col=1)

df_all_openings = pd.DataFrame(summary_of_all_eco_openings)
df_all_openings = df_all_openings.rename(columns={
    "_id": "Opening",
    "percent_won": "% won",
    "percent_draw": "% draw",
    "percent_lost": "% lost",
    })
df_all_openings['% won'] = df_all_openings['% won'].apply(lambda x: f"{x:.1f}%")
df_all_openings['% draw'] = df_all_openings['% draw'].apply(lambda x: f"{x:.1f}%")
df_all_openings['% lost'] = df_all_openings['% lost'].apply(lambda x: f"{x:.1f}%")


#########################################################
# Assemble Dashboard
#########################################################
st.title(f"{player}'s stats as of {latest_game_data}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(label="Total Games Played", value=all_games)
col2.metric(label="Games Played as White", value=all_games_as_white)
col3.metric(label="Games Played as Black", value=all_games_as_black)
col4.metric(label="Games Played This Month", value=all_games_played_this_month, delta=all_games_played_this_month-all_games_played_last_month)

st.plotly_chart(ratings_over_time_by_time_class)

col1, col2 = st.columns([2,1])

col1.plotly_chart(bar_chart_of_win_draw_loss_percentage)  
col2.plotly_chart(summary_of_time_controls) 

st.subheader("Game Details")

col1, col2, col3 = st.columns(3)

col1.plotly_chart(game_results_as_white)
col2.plotly_chart(game_results_as_black)
col3.plotly_chart(detailed_time_control_chart)

st.subheader("Opening Details")
st.dataframe(df_all_openings)
# st.metric(label="Total Games Played", value=50)
