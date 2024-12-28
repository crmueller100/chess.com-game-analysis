import sys
import os
import pymongo 
from pprint import pprint
import yaml

from connect_to_mongo import connect_to_mongo
from get_player_data import get_player_game_archives, save_player_game_archives, get_player_data
from insert_games_into_mongo import insert_games_into_mongo


def process_player(player, config):
    """Fetches, saves, and inserts game data for a single player."""
    print(f"\nAnalyzing {player}'s data")

    get_player_data(player)

    game_archives = get_player_game_archives(player)
    save_player_game_archives(player, game_archives, **config)

    client, db, collection = connect_to_mongo()
    insert_games_into_mongo(client, db, collection, player)

    client.close()


def main():
    # Use absolute path for config file so you can execute from any directory
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml')

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    pull_player_data = config.get('pull_player_data', [])

    for player in pull_player_data:
        process_player(player, config)  # Process each player


if __name__ == "__main__":
    main()
