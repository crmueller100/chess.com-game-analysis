import os
import json
import pymongo
from pymongo.errors import DuplicateKeyError



def insert_games_into_mongo(client, db, collection, player):
    rootdir = f"../data/game_archives/{player}"

    for monthly_games in os.listdir(rootdir):
        try:
            with open(f"{rootdir}/{monthly_games}", "r") as f:
                data = json.load(f)
                games = data.get("games", [])

                for game in games:
                    try:
                        # The URL will be the default unique identifier (_id). Could use the UUID with collection.insert_one({"_id": game["uuid"], **game}) 
                        collection.insert_one({"_id": game["uuid"], "player": player, **game}) 

                    except DuplicateKeyError:
                        print(f"Duplicate game found (skipping): {game.get('url')}")  

        except FileNotFoundError:
            print(f"File not found: {monthly_games}")




# # print(db.list_collection_names())
# # print(collection.totalSize())

# # Insert a document into the collection
# game1 = {"url": "https://www.chess.com/game/live/692667823"}
# collection.insert_one(game1)
# # collection.insert_one(game1)
# # print(collection.find())
# # for x in collection.find():
#     # print(x)

# if __name__ == "__main__":
#     print("Connected to MongoDB")