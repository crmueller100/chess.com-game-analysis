import sys
import os
import pymongo 
from pprint import pprint
import yaml


from connect_to_mongo import connect_to_mongo
from get_player_data import get_player_game_archives, save_player_game_archives
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
    
    # query the player's game history
    # game_archives = get_player_game_archives(player)
    # save_player_game_archives(player, game_archives)

    # Connect to MongoDB
    # client, db, collection  = connect_to_mongo()

    # load the data
    # insert_games_into_mongo(client, db, collection, player)

    # analyze_player_data(db, collection, player)
    
    # TODO: Delete! This is only a test
    # print('hello')
    # all_games = collection.find({"yyyy_mm": "2014_01"})

    # collection.delete_many({"player": 'hikaru'})
    # all_games = collection.find({'player': 'hikaru'})
    # # print(collection.find_one({'_id': '82282996-91e2-11de-8000-000000010001'}))
    # for game in all_games:
    #     pprint(game)
    #     # print(game)
    #     break
    
    

if __name__ == "__main__":
    main()