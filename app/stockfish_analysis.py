import asyncio
import chess
import chess.engine
import os 
import io
from pprint import pprint
import yaml

import chess.pgn 
from connect_to_mongo import connect_to_mongo

async def analyze_wdl_with_stockfish() -> None:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    player = config.get('username')
    stockfish_time_limit = config.get('stockfish_time_limit', 0.1)
    overwrite_stockfish_analysis = config.get('overwrite_stockfish_analysis', False)
    wdl_blunder_threshold = config.get('wdl_blunder_threshold', 0.5)
    wdl_mistake_threshold = config.get('wdl_blunder_threshold', 0.2)
    wdl_inaccuracy_threshold = config.get('wdl_blunder_threshold', 0.1)

    client, db, collection  = connect_to_mongo()

    # TODO: Make this a configurable value
    g = collection.find_one({'player': player})
    
    if g is None:
        print(f"No game data found for player {player}")
        return

    pgn = g['pgn']
    player_color = 'white' if g['player'].lower() == g['white']['username'].lower() else 'black'

    existing_data = g['player_expectation'] if 'player_expectation' in g else None

    # If the analysis has already been done, don't do it again. 
    if existing_data:
        print(f"Stockfish analysis already done for the selected game with {player} as {player_color}")
        return

    game = chess.pgn.read_game(io.StringIO(pgn))  

    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")
    transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)

    board = game.board()

    white_expectation = []
    black_expectation = []

    print("Analyzing game...")
    for move in game.mainline_moves():
        info = await engine.analyse(board, chess.engine.Limit(time=stockfish_time_limit))

        white_expectation.append(info["score"].white().wdl().expectation())
        black_expectation.append(info["score"].black().wdl().expectation())

        board.push(move)
    await engine.quit()

    player_expectation = white_expectation if player_color == 'white' else black_expectation
    # print("Players's expectation of winning:", player_expectation)
    
    filter_query = {'_id': g['_id']}

    if overwrite_stockfish_analysis: 
        update_operation = {'$set': {f"player_expectation": player_expectation}}
    else:
        update_operation = {'$setOnInsert': {f"player_expectation": player_expectation}}

    result = collection.update_one(filter_query, update_operation, upsert=False)

    print(f"modified_count: {result.modified_count}")
    if result.modified_count > 0:
        print(f"Updated document with _id: {g['_id']} for {player_color}")
    else:
        print(f"No changes made to document with _id: {g['_id']} for {player_color} (player_expectation might already exist)")


    # Calculate the number of blunders, mistakes and inaccuracies
    num_blunders = 0
    num_mistakes = 0
    num_inaccuracies = 0

    for i in range(1, len(player_expectation)):
        wdl_change = player_expectation[i] - player_expectation[i-1]

        if wdl_change > wdl_blunder_threshold:
            num_blunders +=1 
        elif wdl_change > wdl_mistake_threshold:
            num_mistakes += 1
        elif wdl_change > wdl_inaccuracy_threshold:
            num_inaccuracies += 1

    if overwrite_stockfish_analysis: 
        update_operation = {
            '$set': {
                "num_blunders": num_blunders,
                "num_mistakes": num_mistakes,
                "num_inaccuracies": num_inaccuracies
                }
            }
    else:
        update_operation = {
            '$setOnInsert': {
                "num_blunders": num_blunders,
                "num_mistakes": num_mistakes,
                "num_inaccuracies": num_inaccuracies
                }
            }

    result = collection.update_one(filter_query, update_operation, upsert=False) # uses same filter_query as above


    client.close()

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml')
    asyncio.run(analyze_wdl_with_stockfish())

