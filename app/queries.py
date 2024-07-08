import pymongo
from connect_to_mongo import connect_to_mongo
from datetime import datetime

# TODO: delete this 
client, db, collection  = connect_to_mongo()

def get_all_games(collection, player, time_class=None, color=None):
    filter_query = { "player": player }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}

    return collection.count_documents(filter_query)

def get_all_games_as_white(collection, player, time_class=None, color=None):
    filter_query = {
        # makes it a case-insensitive search
        "white.username": {"$regex": f"^{player}$", "$options": "i"},
        "player": player
    }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}

    return collection.count_documents(filter_query)

def get_all_games_as_black(collection, player, time_class=None, color=None):
    filter_query = {
        # makes it a case-insensitive search
        "black.username": {"$regex": f"^{player}$", "$options": "i"},
        "player": player
    }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}

    return collection.count_documents(filter_query)

def get_all_games_played_in_a_month(collection, player, month, time_class=None, color=None):
    filter_query = {
        "player": player,
        "month": month
    }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}

    return collection.count_documents(filter_query)


def get_win_loss_counts(collection, player, color, time_class=None, color_filter=None):

    pipeline = [
        {
            "$match": {
                f"{color}.username": {"$regex": player, "$options": "i"},
                **({"time_class": time_class} if time_class else {}),
                **({f"{color_filter}.username": {"$regex": f"^{player}$", "$options": "i"}} if color_filter else {})
                
            }
        },
        {
            # This creates a new field called "result" that contains the value of "{color}.result"
            "$project": { 
                "result": f"${color}.result"
            }
        },
        {
            "$group": {
                "_id": "$result",
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result

def count_time_controls(collection, player, time_class=None, color=None):
    pipeline = [
        {
            "$match": {
                f"player": {"$regex": player, "$options": "i"},
                **({"time_class": time_class} if time_class else {}),
                **({f"{color}.username": {"$regex": f"^{player}$", "$options": "i"}} if color else {})
            }
        },
        {
            "$project": { 
                "result": "$time_class"
            }
        },
        {
            "$group": {
                "_id": "$result",
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result