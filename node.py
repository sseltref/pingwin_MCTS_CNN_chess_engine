import random
from functions import*
class treeNode():
    def __init__(self, board, parent, move_bias,n_init,bias_constant):
        self.calls=0
        self.board=board
        self.sideToMove = board.turn
        self.parent = parent
        self.numVisits = n_init
        self.totalReward = 0
        self.minmaxReward = -1
        self.children = {}
        self.move_bias = move_bias
        self.add_node_picked = True
        self.last_added_node = None
        self.num_children = 0
        self.legal_moves=list(board.legal_moves)
        self.splitted_dims_board = split_dims(self.board, self.legal_moves)
        if bias_constant>0:
            self.from_move_prob_dist_dict = get_piece_board(self.board, self.splitted_dims_board,self.legal_moves)[0]
        self.num_of_legal_moves = len(list(self.legal_moves))
        self.isTerminal = self.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.iterations_sice_expanded = 0
        possible_actions=self.legal_moves
        random.shuffle(possible_actions)
        self.possible_actions=possible_actions
    def takeAction(self, move):
        new_board = copy.deepcopy(self.board)
        new_board.push(move)
        return new_board
    def isTerminal(self):
        if self.num_of_legal_moves==0:
            return True
        else:
            return False