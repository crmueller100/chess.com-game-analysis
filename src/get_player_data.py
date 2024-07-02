import requests
import os
import json

from datetime import datetime

headers = {
    "User-Agent": "curl/8.4.0"
    }

def get_player_game_archives(player):
    url = f"https://api.chess.com/pub/player/{player}/games/archives"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        game_archives = response.json()
    else:
        print("Error:", response)
    
    years, months = divmod(len(game_archives['archives']),12)
    print(f"Player {player} has been on Chess.com for {years} years and {months} months")

    return game_archives

def save_player_game_archives(player, game_archives):
    os.makedirs(f"game_archives/{player}", exist_ok=True)
    # TODO: remove the [:3] to get all the games
    for game in game_archives['archives'][:3]:
        year = game.split('/')[-2]
        month = game.split('/')[-1]
        # If the file doesn't exist, create it. If it's in the past, we know the data won't change. If it's the current month, we want to update it.
        if not os.path.exists(f"game_archives/{player}/{year}_{month}.json") or (int(year) == datetime.today().year and int(month) == datetime.today().month):
            url = f"https://api.chess.com/pub/player/{player}/games/{year}/{month}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                games = response.json()
                with open(f"game_archives/{player}/{year}_{month}.json", "w") as f:
                    f.write(json.dumps(games, indent=2))
                    print(f"Saved {year}_{month}.json for {player}")
            else:
                print("Error:", response)
    

# # print(db.list_collection_names())
# # print(collection.totalSize())

# # Insert a document into the collection
# game1 = {"url": "https://www.chess.com/game/live/692667823"}
# collection.insert_one(game1)
# # collection.insert_one(game1)
# # print(collection.find())
# # for x in collection.find():
#     # print(x)

# if __name__ == "__main__":
#     print("Connected to MongoDB")