from connect_to_mongo import connect_to_mongo
from get_player_data import get_player_game_archives, save_player_game_archives

def main():
    # Connect to MongoDB
    client, db, collection  = connect_to_mongo()
    
    player = 'hikaru'
    url = f'https://api.chess.com/pub/player/{player}/'
    stats_url = f'https://api.chess.com/pub/player/{player}/stats'
    
    url = f"https://api.chess.com/pub/player/{player}/games/2014/01"
    
    game_archives = get_player_game_archives(player)
    save_player_game_archives(player, game_archives)


if __name__ == "__main__":
    main()