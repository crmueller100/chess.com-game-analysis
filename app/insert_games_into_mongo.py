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
                yyyy_mm = monthly_games[:-5]
                
                insert_count = 0
                duplicate_count = 0
                for game in games:
                    try:
                        # The URL will be the default unique identifier (_id). Could use the UUID with collection.insert_one({"_id": game["uuid"], **game}) 
                        collection.insert_one({"_id": game["uuid"], "player": player.lower(), "month": yyyy_mm, **game}) 
                        # print(f"Inserted yyyy_mm {yyyy_mm} for player {player}")
                        insert_count += 1
                    except DuplicateKeyError:
                        # print(f"Duplicate game found (skipping): {game.get('url')}")  
                        duplicate_count += 1
                print(f"Inserted {insert_count} games and skipped {duplicate_count} duplicates for {player} in {yyyy_mm}")
        except FileNotFoundError:
            print(f"File not found: {monthly_games}")
