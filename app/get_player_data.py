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

def get_player_data(player, **kwargs):
    if kwargs:
        player = kwargs["params"].get("player_username", player)

    print(f"Getting data for player {player}")

    url = f"https://api.chess.com/pub/player/{player}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Request failed with status code " + str(response.status_code))
        raise ValueError("Please check the player username and try again.")

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
        ]
        '''
    else:
        raise ValueError("Unable to get game archives for player " + player)
    
    years, months = divmod(len(game_archives['archives']),12)
    print(f"Player {player} has been on Chess.com for {years} years and {months} months")

    return game_archives

def save_player_game_archives(player, game_archives, **kwargs):

    # All historical data should be complete months EXCEPT the most recent month. We can't be sure that the most recent month is a full set of data.
    # e.g. If we pull data on July 15th, then don't run the script until August, then July will only have half its data.
    # So we need to determine the LATEST month we have stored for each player and pull that + all future months.

    data_dir = os.getenv("DATA_DIR", "../data")
    player_directory = os.path.join(data_dir, f"game_archives/{player}")

    os.makedirs(player_directory, exist_ok=True)

    refresh_entire_history = kwargs.get('refresh_entire_history', False)

    files = os.listdir(player_directory)
    date_pattern = re.compile(r'(\d{4})_(\d{2})\.json$')
    files_with_dates = []

    for file in files:
        match = date_pattern.search(file)
        if match:
            files_with_dates.append((file, match.group(1), match.group(2)))

    files_with_dates.sort(key=lambda x: (x[1], x[2]), reverse=True) # in the format [('2014_03.json', '2014', '03'), ('2014_02.json', '2014', '02'), ...]

    # If you're pulling data from a new player, there will be no files_with_dates. This handles that case
    if files_with_dates:
        latest_file = files_with_dates[0][0] # This is the latest file. It's in the format of 'YYYY_MM.json'. We'll match it with all months to see which is the latest
    else:
        latest_file = None

    for game in game_archives['archives']:
        year = game.split('/')[-2]
        month = game.split('/')[-1]

        # If the player doesn't have a directory for that month, it's the latest month, or the hard_refresh_player_history flag is set to True, then we need to write the data to storage
        if not os.path.exists(os.path.join(player_directory, f"{year}_{month}.json")) or f"{year}_{month}.json" == latest_file or refresh_entire_history:
            url = f"https://api.chess.com/pub/player/{player}/games/{year}/{month}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                games = response.json()
                with open(os.path.join(player_directory, f"{year}_{month}.json"), "w") as f:
                    f.write(json.dumps(games, indent=2))
                    print(f"Saved {year}_{month}.json for {player}")
            else:
                print("Error:", response)
