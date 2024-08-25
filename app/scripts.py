#############################################
# This file is simply a record of one-off scripts I ran to clean, delete, and otherwise transform the data
#############################################


import sys
import os
import pymongo 
from pprint import pprint
import yaml


from connect_to_mongo import connect_to_mongo
from get_player_data import get_player_game_archives, save_player_game_archives, get_player_data
from insert_games_into_mongo import insert_games_into_mongo

import chess.pgn 
import io
from eco_code_mappings import eco_code_mappings

def query_game():    
    client, db, collection  = connect_to_mongo()

    # results = collection.find_one({"_id": "f258e012-aaf5-11e3-8088-00000001000b"})
    results = collection.find_one({'eco_opening': {'$eq': None}})
    pprint(results)

def update_all_player_history_with_eco_codes():    
    # Connect to MongoDB
    client, db, collection  = connect_to_mongo()

    # load the data into MongoDB
    results = collection.find({'eco_opening': {'$eq': None}})
    num_records = 0
    for game in results:
        if num_records % 100 == 0:
            print(f"Processing game number {num_records}")
        num_records += 1
        pgn = game.get("pgn")
        pgn_game = chess.pgn.read_game(io.StringIO(pgn))
        eco_code = pgn_game.headers.get('ECO')
        if eco_code:
            eco_opening = eco_code_mappings.get(eco_code, "Code does not exist")
            eco_opening_general = eco_opening.split(",")[0]  # Get the opening without the variant
        else:
            eco_opening = "ECO Code Missing"
            eco_opening_general = "ECO Code Missing"
        update_operation = {
            '$set': {
                "eco_opening": eco_opening,
                "eco_opening_general": eco_opening_general
                }
            }

        collection.update_one({'_id': game['_id']}, update_operation)
    

    client.close() 
        
if __name__ == "__main__":
    query_game()
    # update_all_player_history_with_eco_codes()