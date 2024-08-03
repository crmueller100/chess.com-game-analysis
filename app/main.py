import sys
import os
import pymongo 
from pprint import pprint
import yaml


from connect_to_mongo import connect_to_mongo
from get_player_data import get_player_game_archives, save_player_game_archives, get_player_data
from insert_games_into_mongo import insert_games_into_mongo

def main():    
    # Use absolute path for config file so you can execute from any directory
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml')

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    player = config.get('username')
    refresh_entire_history = config.get('refresh_entire_history', False)

    if not player:
        print('Please set a username in the config file')
        sys.exit()
    else:
        print(f"Analyzing {player}'s data")
    
    get_player_data(player)
    
    # query the player's game history
    game_archives = get_player_game_archives(player)
    save_player_game_archives(player, game_archives, **config)

    # Connect to MongoDB
    client, db, collection  = connect_to_mongo()

    # load the data into MongoDB
    insert_games_into_mongo(client, db, collection, player)
    

if __name__ == "__main__":
    main()