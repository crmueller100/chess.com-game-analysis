import requests
import os
import json

from datetime import datetime
# url = 'https://api.chess.com/pub/player/hikaru'
# stats_url = 'https://api.chess.com/pub/player/hikaru/stats'

player = 'hikaru'
url = "https://api.chess.com/pub/player/hikaru/games/2014/01"
headers = {
    "User-Agent": "curl/8.4.0"
    }

MONGO_HOST = os.getenv('MONGO_HOST')

def get_player_game_archives(player):
    url = f"https://api.chess.com/pub/player/{player}/games/archives"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        game_archives = response.json()
    else:
        print("Error:", response)
    
    years, months = divmod(len(game_archives['archives']),12)
    print(f"Player {player} has been on Chess.com for {years} years and {months} months")

    save_player_game_archives(player, game_archives)

def save_player_game_archives(player, game_archives):
    os.makedirs(f"game_archives/{player}", exist_ok=True)
    # TODO: remove the [:3] to get all the games
    for game in game_archives['archives'][:3]:
        year = game.split('/')[-2]
        month = game.split('/')[-1]
        if not os.path.exists(f"game_archives/{player}/{year}_{month}.json") or (int(year) == datetime.today().year and int(month) == datetime.today().month):
            url = f"https://api.chess.com/pub/player/{player}/games/{year}/{month}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                games = response.json()
                with open(f"game_archives/{player}/{year}_{month}.json", "w") as f:
                    f.write(json.dumps(games, indent=2))
            else:
                print("Error:", response)
    


get_player_game_archives(player)
