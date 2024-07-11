import requests
import os
import json

from datetime import datetime

headers = {
    "User-Agent": "curl/8.4.0"
    }

'''
url = f'https://api.chess.com/pub/player/{player}/'
stats_url = f'https://api.chess.com/pub/player/{player}/stats'
url = f"https://api.chess.com/pub/player/{player}/games/2014/01"
'''

def get_player_data(player):
    url = f"https://api.chess.com/pub/player/{player}"
    response = requests.get(url, headers=headers)

    # check if reponse.status_code is 200
    return response

def get_player_game_archives(player):
    url = f"https://api.chess.com/pub/player/{player}/games/archives"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        game_archives = response.json()
        '''
        The response is an array of the following format:
        [
        https://api.chess.com/pub/player/hikaru/games/2014/01,
        https://api.chess.com/pub/player/hikaru/games/2014/02,
        ... 
        'https://api.chess.com/pub/player/hikaru/games/2024/06',
        'https://api.chess.com/pub/player/hikaru/games/2024/07',
        ]
        '''
    else:
        print("Error:", response)
    
    years, months = divmod(len(game_archives['archives']),12)
    print(f"Player {player} has been on Chess.com for {years} years and {months} months")

    return game_archives

def save_player_game_archives(player, game_archives):
    os.makedirs(f"../data/game_archives/{player}", exist_ok=True)
    # TODO: remove the [:3] to get all the games
    for game in game_archives['archives'][:3]:
        year = game.split('/')[-2]
        month = game.split('/')[-1]
        # TODO: We need to update the LATEST month, not just the current month. If we haven't ran this for a couple months, then we'll need to pull data for the remained of the last month we have plus all future months
        # If the file doesn't exist, create it. If it's in the past, we know the data won't change. If it's the current month, we want to update it.
        if not os.path.exists(f"../data/game_archives/{player}/{year}_{month}.json") or (int(year) == datetime.today().year and int(month) == datetime.today().month):
            url = f"https://api.chess.com/pub/player/{player}/games/{year}/{month}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                games = response.json()
                with open(f"../data/game_archives/{player}/{year}_{month}.json", "w") as f:
                    f.write(json.dumps(games, indent=2))
                    print(f"Saved {year}_{month}.json for {player}")
            else:
                print("Error:", response)
