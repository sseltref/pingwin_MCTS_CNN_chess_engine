import gc
from mcts import mcts
import chess
from node import treeNode
import sys, subprocess

class pingwin_game:
    def __init__(self, exploration_constant, bias_constant,n_init,initboard,killer_rate,  time_limit=10, simulation_depth=0, mirror = False):
        self.moves_made=0
        self.mirror = mirror
        self.simulation_depth=simulation_depth
        self.time_limit = time_limit
        self.E = exploration_constant
        self.B = bias_constant
        self.killer_rate=killer_rate
        self.board = initboard
        self.n_init=n_init
        self.searcher = mcts(initialState=self.board, timeLimit=self.time_limit * 1000, explorationConstant=self.E,
                             biasConstant=self.B, n_init=self.n_init, killer_rate=self.killer_rate, simulation_depth=self.simulation_depth)
    def search_for_move(self):
        action = self.searcher.search()
        return action
    def make_move(self, time):
        self.searcher.timeLimit = time*1000
        action = self.search_for_move()
        self.board.push(action)
        self.searcher.print_analysis(self.board,0)
        self.searcher.root = self.searcher.bestChildVisit
        self.searcher.root.parent = None
        gc.collect()
        self.moves_made+=1
        print("Computer move: ")
        print(action.uci())
        print("")
        return action.uci()
    def read_opponent_move(self,move):
        if move == None:
            move = input("Input your move: ")
            subprocess.run('cls', shell=True)
        else:
            move=move
        move = chess.Move.from_uci(move)
        while move not in self.board.legal_moves:
            move =input("This move is not legal in this position! Insert legal move: ")
            move = chess.Move.from_uci(move)
            subprocess.run('cls', shell=True)
        self.board.push(move)
        with open('last_game_notation.txt', 'w') as f:
            f.write(str(chess.Board().variation_san(self.board.move_stack)))
        for child_move, child_node in self.searcher.root.children.items():
            if child_move == move:
                self.searcher.root = child_node
                self.searcher.root.parent = None
                gc.collect()
                return
        self.searcher.root = treeNode(self.board, None, 0, 0,self.B)
        return
    def play(self):
        while True:
            self.make_move(self.time_limit)
            self.read_opponent_move(None)
'''initboard=chess.Board()
time = 10
opponent1=pingwin_game(1, 1, 1,initboard,0.5, time)
opponent1.make_move(time)
board=copy.deepcopy(opponent1.board)
opponent2=pingwin_game(0,1, 1,board,0.5,time)
while True:
    move = opponent2.make_move(time)
    opponent1.read_opponent_move(move)
    print(opponent1.board.move_stack)
    move = opponent1.make_move(time)
    opponent2.read_opponent_move(move)
    print(opponent2.board.move_stack)'''





'''while not chess_game.board.is_game_over():
    chess_game.make_move(10)
    print(chess_game.board.move_stack)'''
'''import cProfile
def go():
  board = chess.Board()
  initialState = board
  searcher = mcts(initialState = initialState, timeLimit=60000, explorationConstant= 1, biasConstant=1,killer_rate=0.5,n_init=1)
  searcher.search()
cProfile.run('go()',sort='cumtime')'''

