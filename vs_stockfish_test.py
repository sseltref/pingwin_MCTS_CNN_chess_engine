from stockfish import Stockfish
import chess
import subprocess
import gc
from main import pingwin_game
stockfish = Stockfish(path="C:/Users/Oliwia/PycharmProjects/chess_engine/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe", parameters={"Skill Level": 6})
settings_file = 'settings.txt'
settings={}
with open(settings_file) as f:
    for line in f:
        (key, val) = line.strip().split(' = ')
        settings[key] = val
subprocess.run('cls', shell=True)
board=chess.Board()
print(board)
time = 600


#move = input("Input your move: ")
#move = chess.Move.from_uci(move)
#initboard.push(move)


chess_game = pingwin_game(exploration_constant=float(settings['exploration_constant']),bias_constant=float(settings['bias_constant']),n_init=int(settings['init_node_visits']),initboard=board,killer_rate=float(settings['killer_rate']), time_limit=time, simulation_depth=int(settings['simulation_depth']), print_limit=int(settings['moves_print_limit']), show_variation=settings['show_best_line'])
while True:
    gc.collect()
    chess_game.make_move(60)
    board_fen = chess_game.board.fen()
    stockfish.set_fen_position(board_fen)
    stockfish_move = str(stockfish.get_best_move())
    chess_game.read_opponent_move(stockfish_move)