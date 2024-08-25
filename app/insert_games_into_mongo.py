import os
import json
import pymongo
from datetime import datetime

from pymongo.errors import DuplicateKeyError
from pprint import pprint

import chess.pgn 
import io
from eco_code_mappings import eco_code_mappings

def get_latest_game_in_database(client, db, collection, player):
    latest_month = collection.find_one({'player': player.lower()}, sort=[('month', pymongo.DESCENDING)], projection={"month": 1})
    if latest_month is None:
        return '2000_01'
    return latest_month['month']

def insert_games_into_mongo(client, db, collection, player):
    data_dir = os.getenv("DATA_DIR", "../data")
    player_directory = os.path.join(data_dir, f"game_archives/{player}")

    latest_month = get_latest_game_in_database(client, db, collection, player) # formated as YYYY_MM
    if not latest_month:
        latest_month = '2000_01' # If no games are found, start earlier than chess.com was founded

    for monthly_games in os.listdir(player_directory):
        yyyy_mm = monthly_games[:-5] # Remove the .json extension
        
        yyyy_mm_datetime = datetime.strptime(yyyy_mm, "%Y_%m")
        latest_month_datetime = datetime.strptime(latest_month, "%Y_%m")
        
        if yyyy_mm_datetime >= latest_month_datetime: # If the directory is the same or newer than the latest month in the database, insert the games
            try:
                with open(f"{player_directory}/{monthly_games}", "r") as f:
                    file_content = f.read().strip()
                    if file_content: # Check if the file is empty
                        f.seek(0)
                        data = json.load(f)
                        games = data.get("games", [])
                        
                        insert_count = 0
                        duplicate_count = 0
                        for game in games: # game type is <class 'dict'>
                            try:
                                if game.get("rules") == "chess": # Don't want to include other variants (bughouse, kingofthehill, 3check, etc...)

                                    # lookup the opening
                                    pgn = game.get("pgn")
                                    pgn_game = chess.pgn.read_game(io.StringIO(pgn))
                                    eco_code = pgn_game.headers.get('ECO')
                                    if eco_code:
                                        eco_opening = eco_code_mappings.get(eco_code, "Code does not exist")
                                        eco_opening_general = eco_opening.split(",")[0]  # Get the opening without the variant
                                    else:
                                        eco_opening = "ECO Code Missing"
                                        eco_opening_general = "ECO Code Missing"

                                    # The URL will be the default unique identifier (_id). Could use the UUID with collection.insert_one({"_id": game["uuid"], **game}) 
                                    collection.insert_one({"_id": game["uuid"],
                                                            "player": player.lower(),
                                                            "month": yyyy_mm,
                                                            "eco_opening": eco_opening,
                                                            "eco_opening_general": eco_opening_general,
                                                            **game}) 
                                    # print(f"Inserted yyyy_mm {yyyy_mm} for player {player}")
                                    insert_count += 1
                            except DuplicateKeyError:
                                # print(f"Duplicate game found (skipping): {game.get('url')}")  
                                duplicate_count += 1
                        print(f"Inserted {insert_count} games and skipped {duplicate_count} duplicates for {player} in {yyyy_mm}")
            except FileNotFoundError:
                print(f"File not found: {monthly_games}")
