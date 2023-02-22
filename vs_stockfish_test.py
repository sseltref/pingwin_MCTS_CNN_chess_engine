from stockfish import Stockfish
import chess
import subprocess
import gc
import numpy as np
from main import pingwin_game
settings_file = 'settings.txt'
settings={}
with open(settings_file) as f:
    for line in f:
        (key, val) = line.strip().split(' = ')
        settings[key] = val
subprocess.run('cls', shell=True)


#move = input("Input your move: ")
#move = chess.Move.from_uci(move)
#initboard.push(move)
elo = 2000
number=0
while True:
    try:
        stockfish = Stockfish(
            path="",
            parameters={"UCI_LimitStrength": "true",
                        "UCI_Elo": elo})
        result = 'playing'
        color =['w', 'b']
        color = np.random.choice(color)
        if color == 'b':
            board = chess.Board()
            board_fen = board.fen()
            stockfish.set_fen_position(board_fen)
            stockfish_move = chess.Move.from_uci(str(stockfish.get_best_move()))
            board.push(stockfish_move)
        else:
            board = chess.Board()
        time = 10
        new_elo = elo
        chess_game = pingwin_game(exploration_constant=float(settings['exploration_constant']),bias_constant=float(settings['bias_constant']),n_init=int(settings['init_node_visits']),initboard=board,killer_rate=float(settings['killer_rate']), time_limit=time, simulation_depth=int(settings['simulation_depth']), print_limit=int(settings['moves_print_limit']), show_variation=settings['show_best_line'])
        while True:
            gc.collect()
            chess_game.make_move(300)
            if chess_game.board.can_claim_draw() == True or chess_game.board.is_stalemate() == True or chess_game.board.is_insufficient_material() == True:
                result = 'draw'
                break
            if chess_game.board.is_checkmate() == True or chess_game.is_winning == True:
                result = 'win'
                elo+=50
                break
            board_fen = chess_game.board.fen()
            stockfish.set_fen_position(board_fen)
            stockfish_move = str(stockfish.get_best_move())
            chess_game.read_opponent_move(stockfish_move)
            if chess_game.board.is_checkmate() == True or chess_game.is_losing == True:
                result = 'loss'
                elo-=50
                break
        number+=1
        with open('experiment_300_sek/elo{}_{}_{}_{}.txt'.format(new_elo, result,color,number), 'w') as f:
            f.write(str(chess.Board().variation_san(chess_game.board.move_stack)))
    except:
        print('error')