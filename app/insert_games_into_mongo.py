import os
import json
import pymongo
from pymongo.errors import DuplicateKeyError
from pprint import pprint

from datetime import datetime

def get_latest_game_in_database(client, db, collection, player):
    latest_month = collection.find_one({'player': player.lower()}, sort=[('month', pymongo.DESCENDING)], projection={"month": 1})
    return latest_month['month']

def insert_games_into_mongo(client, db, collection, player):
    rootdir = f"../data/game_archives/{player}"

    latest_month = get_latest_game_in_database(client, db, collection, player) # formated as YYYY_MM
    if not latest_month:
        latest_month = '2000_01' # If no games are found, start earlier than chess.com was founded

    for monthly_games in os.listdir(rootdir):
        yyyy_mm = monthly_games[:-5]
        
        yyyy_mm_datetime = datetime.strptime(yyyy_mm, "%Y_%m")
        latest_month_datetime = datetime.strptime(latest_month, "%Y_%m")
        
        if yyyy_mm_datetime >= latest_month_datetime: # If the directory is the same or newer than the latest month in the database, insert the games
            try:
                with open(f"{rootdir}/{monthly_games}", "r") as f:
                    file_content = f.read().strip()
                    if file_content: # Check if the file is empty
                        f.seek(0)
                        data = json.load(f)
                        games = data.get("games", [])
                        
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
