import asyncio
import chess
import chess.engine
import os 
import io
from pprint import pprint

import chess.pgn 
from connect_to_mongo import connect_to_mongo

async def main() -> None:
    client, db, collection  = connect_to_mongo()
    x = collection.find_one()
    pgn = x['pgn']
    
    player_color = 'white' if x['player'] in x['white'].keys() else 'black'

    game = chess.pgn.read_game(io.StringIO(pgn))  

    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")
    transport, engine = await chess.engine.popen_uci(STOCKFISH_PATH)

    board = game.board()

    white_cp = []
    black_cp = []

    white_expectation = []
    black_expectation = []

    count = 0
    for move in game.mainline_moves():
        # print(count)
        count += 1
        info = await engine.analyse(board, chess.engine.Limit(time=0.01)) # TODO: Change this back to 0.1

        white_expectation.append(info["score"].white().wdl().expectation())
        black_expectation.append(info["score"].black().wdl().expectation())
        if board.turn == chess.WHITE:
            if info["score"].white().score() is not None: # The score will be None if there is a forced mate
                white_cp.append(info["score"].white().score()) # Positive for White's advantage
        else:
            if info["score"].black().score() is not None:
                black_cp.append(-info["score"].black().score())  # Negate for Black's advantage
        board.push(move)
    await engine.quit()

    print("White's expectation of winning:", white_expectation)
    print("White's cp:", white_cp)
    print("White's expectation of winning:", white_expectation)
    print("Black's cp:", black_cp)

asyncio.run(main())
