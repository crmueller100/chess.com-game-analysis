import asyncio
import chess
import chess.engine
import os 
import io
from pprint import pprint

import chess.pgn 
from connect_to_mongo import connect_to_mongo

async def analyze_wdl_with_stockfish() -> None:
    client, db, collection  = connect_to_mongo()
    x = collection.find_one()
    pgn = x['pgn']
    player_color = 'white' if x['player'].lower() == x['white']['username'].lower() else 'black'
    # pprint(x)
    game = chess.pgn.read_game(io.StringIO(pgn))  

    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")
    transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)

    board = game.board()

    white_expectation = []
    black_expectation = []

    for move in game.mainline_moves():
        # Don't set the time parameter smaller than 0.1. It will cause the engine to think one side is winning when it isn't because it can't calculate far enough ahead
        info = await engine.analyse(board, chess.engine.Limit(time=0.01)) # TODO: Change this back to 0.1

        white_expectation.append(info["score"].white().wdl().expectation())
        black_expectation.append(info["score"].black().wdl().expectation())

        board.push(move)
    await engine.quit()

    # print("\n\nWhite's expectation of winning:", white_expectation)
    # print("Black's expectation of winning:", black_expectation)


    player_expectation = white_expectation if player_color == 'white' else black_expectation
    
    filter_query = {'_id': x['_id']}
    update_operation = {'$set': {f"player_expectation": player_expectation}}

    result = collection.update_one(filter_query, update_operation, upsert=False)

    print(f"modified_count: {result.modified_count}")
    if result.modified_count > 0:
        print(f"Updated document with _id: {x['_id']} for {player_color}")
    else:
        print(f"Failed to update document with _id: {x['_id']} for {player_color}")

    client.close()

if __name__ == "__main__":
    asyncio.run(analyze_wdl_with_stockfish())

