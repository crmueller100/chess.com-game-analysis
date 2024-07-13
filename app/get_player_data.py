import requests
import os
import json
import re

from pprint import pprint 

from datetime import datetime

from connect_to_mongo import connect_to_mongo

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
    
    # All historical data should be complete months EXCEPT the most recent month. We can't be sure that the most recent month is a full set of data.
    # e.g. If we pull data on July 15th, then don't run the script until August, then July will only have half its data.
    # So we need to determine the LATEST month we have stored for each player and pull that + all future months.
    os.makedirs(f"../data/game_archives/{player}", exist_ok=True)
    player_directory = f"../data/game_archives/{player}/"

    files = os.listdir(player_directory)
    date_pattern = re.compile(r'(\d{4})_(\d{2})\.json$')
    files_with_dates = []

    for file in files:
        match = date_pattern.search(file)
        if match:
            files_with_dates.append((file, match.group(1), match.group(2)))

    files_with_dates.sort(key=lambda x: (x[1], x[2]), reverse=True) # in the format [('2014_03.json', '2014', '03'), ('2014_02.json', '2014', '02'), ...]
    latest_file = files_with_dates[0][0] # This is the latest file. It's in the format of 'YYYY_MM.json'. We'll match it with all months to see which is the latest

    # TODO: remove the [:10] to get all the games
    for game in game_archives['archives'][:10]:
        year = game.split('/')[-2]
        month = game.split('/')[-1]

        # If the player doesn't have a directory for that month, it's the latest month, or the hard_refresh_player_history flag is set to True, then we need to write the data to storage
        if not os.path.exists(f"../data/game_archives/{player}/{year}_{month}.json") or f"{year}_{month}.json" == latest_file or os.getenv("HARD_REFRESH_PLAYER_HISTORY", "False").lower() == "true":
            url = f"https://api.chess.com/pub/player/{player}/games/{year}/{month}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                games = response.json()
                with open(f"../data/game_archives/{player}/{year}_{month}.json", "w") as f:
                    f.write(json.dumps(games, indent=2))
                    print(f"Saved {year}_{month}.json for {player}")
            else:
                print("Error:", response)
