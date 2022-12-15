from functions import*
class treeNode():
    def __init__(self, board, parent, move_bias, n_init):
        # state of for the node
        self.board = board
        self.sideToMove = board.turn
        # relations with other nodes
        self.parent = parent
        self.children = {}
        self.numVisits = n_init
        self.totalReward = 0
        self.minmaxReward = -1
        # bias of the node given by CNN
        self.move_bias = move_bias
        self.add_node_picked = True
        self.last_added_node = None
        self.num_children = 0
        self.legal_moves = list(board.legal_moves)
        # array representation of the board
        self.splitted_dims_board = split_dims(self.board, self.legal_moves)
        # dictionary containing keys of available pieces to move and values of probabilities of given piece move being the best
        self.from_move_prob_dist_dict = get_piece_board(self.board, self.splitted_dims_board, self.legal_moves)[0]
        self.num_of_legal_moves = len(list(self.legal_moves))
        self.isTerminal = self.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.iterations_sice_expanded = 0
    # method that generates new state from this node
    def takeAction(self, move):
        new_board = copy.deepcopy(self.board)
        new_board.push(move)
        return new_board

    # method that checks if state of the node is terminal
    def isTerminal(self):
        if self.num_of_legal_moves==0:
            return True
        else:
            return False