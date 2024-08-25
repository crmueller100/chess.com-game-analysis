import asyncio
import chess
import chess.engine
import os 
import io
from pprint import pprint
import yaml

import chess.pgn 
from connect_to_mongo import connect_to_mongo

async def analyze_wdl_with_stockfish(game_id, **config) -> None:
    if game_id is None:
        print(f"Please enter a game_id and re-run.")
        return
    
    stockfish_time_limit = config.get('stockfish_time_limit', 0.1)
    overwrite_stockfish_analysis = config.get('overwrite_stockfish_analysis', False)
    wdl_blunder_threshold = config.get('wdl_blunder_threshold', 0.5)
    wdl_mistake_threshold = config.get('wdl_mistake_threshold', 0.2)
    wdl_inaccuracy_threshold = config.get('wdl_inaccuracy_threshold', 0.1)

    client, db, collection  = connect_to_mongo()

    g = collection.find_one({'_id': game_id})
    
    if g is None:
        print(f"No game data found for that game_id")
        return
    
    # Want to make sure you're using the player whose game_id you're using
    player = g['player']

    pgn = g['pgn']
    player_color = 'white' if g['player'].lower() == g['white']['username'].lower() else 'black'

    existing_data = g['player_expectation'] if 'player_expectation' in g else None

    # If the analysis has already been done, don't do it again. 
    if existing_data and not overwrite_stockfish_analysis:
        print(f"Stockfish analysis already done for the selected game with {player} as {player_color}")
        return

    game = chess.pgn.read_game(io.StringIO(pgn))  

    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")

    print(f"Using STOCKFISH_PATH: {STOCKFISH_PATH}")
    transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)

    board = game.board()

    white_expectation = []
    black_expectation = []

    print("Analyzing game...")
    for move in game.mainline_moves():
        info = await engine.analyse(board, chess.engine.Limit(time=stockfish_time_limit))

        white_expectation.append(round(float(info["score"].white().wdl().expectation()), 2))
        black_expectation.append(round(float(info["score"].black().wdl().expectation()), 2))

        board.push(move)
    await engine.quit()

    player_expectation = white_expectation if player_color == 'white' else black_expectation
    print("Players's expectation of winning:", player_expectation)
    
    filter_query = {'_id': game_id}
    update_operation = {'$set': {f"player_expectation": player_expectation}}

    result = collection.update_one(filter_query, update_operation, upsert=False)

    print(f"modified_count: {result.modified_count}")
    if result.modified_count > 0:
        print(f"Updated document with _id: {game_id} for {player} as {player_color}")
    else:
        print(f"No changes made to document with _id: {game_id} for {player} as {player_color} (player_expectation might already exist)")


    # Calculate the number of blunders, mistakes and inaccuracies
    num_blunders = 0
    num_mistakes = 0
    num_inaccuracies = 0

    for i in range(1, len(player_expectation)):
        wdl_change = player_expectation[i] - player_expectation[i-1]

        if wdl_change >= wdl_blunder_threshold:
            num_blunders +=1 
        elif wdl_change >= wdl_mistake_threshold:
            num_mistakes += 1
        elif wdl_change >= wdl_inaccuracy_threshold:
            num_inaccuracies += 1

    update_operation = {
        '$set': {
            "num_blunders": num_blunders,
            "num_mistakes": num_mistakes,
            "num_inaccuracies": num_inaccuracies
            }
        }

    result = collection.update_one(filter_query, update_operation, upsert=False) # uses same filter_query as above

    client.close()

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Analyzing with Stockfish is built to run using Airflow webserver. Enter a game_id here if you want to run manually
    game_id = "72ef41ac-b62c-11e4-82cc-00000001000b" 
    asyncio.run(analyze_wdl_with_stockfish(game_id, **config))
