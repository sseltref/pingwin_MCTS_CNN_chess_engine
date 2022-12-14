import chess
import subprocess
from main import pingwin_game
settings_file = 'settings.txt'
settings={}
with open(settings_file) as f:
    for line in f:
        (key, val) = line.strip().split(' = ')
        settings[key] = val
subprocess.run('cls', shell=True)
initboard=chess.Board()
print(initboard)
time = int(input("Input time for computer move (in seconds): "))
side = input("Do you want to play as white? (type yes or no): ")
if side == "yes":
    move = input("Input your move: ")
    move = chess.Move.from_uci(move)
    initboard.push(move)
chess_game = pingwin_game(exploration_constant=float(settings['exploration_constant']),bias_constant=float(settings['bias_constant']),n_init=int(settings['init_node_visits']),initboard=initboard,killer_rate=float(settings['killer_rate']), time_limit=time, simulation_depth=int(settings['simulation_depth']))
chess_game.play()