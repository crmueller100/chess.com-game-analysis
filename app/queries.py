import pymongo
from connect_to_mongo import connect_to_mongo
from datetime import datetime

# TODO: delete this 
client, db, collection  = connect_to_mongo()

def get_all_games(collection, player):
    return collection.count_documents({"player": player})

def get_all_games_as_white(collection, player):
    filter_query = {
        # makes it a case-insensitive search
        "white.username": {"$regex": f"^{player}$", "$options": "i"},
        "player": player
    }
    return collection.count_documents(filter_query)

def get_all_games_as_black(collection, player):
    filter_query = {
        # makes it a case-insensitive search
        "black.username": {"$regex": f"^{player}$", "$options": "i"},
        "player": player
    }
    return collection.count_documents(filter_query)

def get_all_games_played_in_a_month(collection, player, month):
    filter_query = {
        "player": player,
        "month": month
    }

    return collection.count_documents(filter_query)


# def get_half_games():
#     """Fetches all games from the collection."""
#     return 5



# from datetime import datetime

# def get_games_this_month(collection):
#     """Fetches games played in the current month."""

#     now = datetime.now()
#     start_of_month = datetime(now.year, now.month, 1)  
#     return 'helo'
#     # games = []
#     # for doc in collection.find():
#     #     for game in doc["games"]:
#     #         game_end_time = datetime.utcfromtimestamp(game["end_time"])  # Convert to datetime
#     #         if game_end_time >= start_of_month:
#     #             games.append(game)
#     # return games
