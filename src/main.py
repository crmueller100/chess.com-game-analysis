import pymongo 

from connect_to_mongo import connect_to_mongo
from get_player_data import get_player_game_archives, save_player_game_archives
from insert_games_into_mongo import insert_games_into_mongo

def main():
    # Connect to MongoDB
    client, db, collection  = connect_to_mongo()
    
    player = 'hikaru'

    game_archives = get_player_game_archives(player)
    save_player_game_archives(player, game_archives)

    insert_games_into_mongo(client, db, collection, player)

    # TODO: Delete! This is only a test
    all_games = collection.find()
    for game in all_games:
        print(game)

if __name__ == "__main__":
    main()