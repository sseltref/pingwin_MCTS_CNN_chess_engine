import keras
import tensorflow
import numpy as np
import statistics
settings_file = 'settings.txt'
settings={}
with open(settings_file) as f:
    for line in f:
        (key, val) = line.strip().split(' = ')
        settings[key] = val
model_evaluation = keras.models.load_model('CNN_models/position_{}.h5'.format(settings['position_eval_neural_network']))
model_piece = keras.models.load_model('CNN_models/piece_{}.h5'.format(settings['bias_neural_network']))
model_move = keras.models.load_model('CNN_models/square_{}.h5'.format(settings['bias_neural_network']))
converter = tensorflow.lite.TFLiteConverter.from_keras_model(model_evaluation)
model_eval_lite = converter.convert()
converter = tensorflow.lite.TFLiteConverter.from_keras_model(model_piece)
model_piece_lite = converter.convert()
converter = tensorflow.lite.TFLiteConverter.from_keras_model(model_move)
model_move_lite = converter.convert()

squares_index = {
  'a': 0,
  'b': 1,
  'c': 2,
  'd': 3,
  'e': 4,
  'f': 5,
  'g': 6,
  'h': 7
}
index_squares = {
    0 :'a',
    1 :'b',
    2 :'c',
    3 :'d',
    4 :'e',
    5 :'f',
    6 :'g',
    7 :'h',
}

chessboard = []
i = 0
while i <8:
  j = 0
  while j < 8:
   chessboard.append(str(i)+str(j))
   j += 1
  i += 1
chessboard = np.array(chessboard)
min_rollout = 0
max_rollout = 0
n_rollouts = 1
def square_to_index(square):
  letter = chess.square_name(square)
  return 8 - int(letter[1]), squares_index[letter[0]]

def split_dims(board, legal_moves):
    board3d = np.zeros((8, 8, 8), dtype=np.int8)
    if board.turn == chess.WHITE:
        v = 1
    else:
        v = -1
    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = np.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = v
        for square in board.pieces(piece, chess.BLACK):
            idx = np.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = -v
    aux = board.turn
    if aux == chess.WHITE:
        white_legal_moves=legal_moves
        board.turn=chess.BLACK
        black_legal_moves=list(board.legal_moves)
    else:
        black_legal_moves=legal_moves
        board.turn=chess.WHITE
        white_legal_moves=list(board.legal_moves)
    board.turn = chess.WHITE
    for move in white_legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[6][i][j] = v
    board.turn = chess.BLACK
    for move in black_legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[7][i][j] = -v
    board.turn = aux
    if v == -1:
        for i in range(len(board3d)):
            flipped_board = np.flipud(board3d[i])
            board3d[i] = flipped_board

    return board3d
def clip_board_pieces(board,legal_moves):
    board2d = np.zeros((8, 8), dtype=np.int8)
    for move in legal_moves:
      i, j = square_to_index(move.from_square)
      board2d[i][j] = 1
    if board.turn == chess.BLACK:
        board2d = np.flipud(board2d)
    return board2d
def get_available_moves_board(board, square,legal_moves):
    from_square = square
    from_move_board = np.zeros((8, 8), dtype=np.int8)
    piece_idx_1 = 8 - int(from_square[1])
    piece_idx_2 = squares_index[from_square[0]]
    from_move_board[piece_idx_1][piece_idx_2] = 1
    available_moves_board = np.zeros((8, 8), dtype=np.int8)
    for move in legal_moves:
        string_move = str(move)[0:2]
        if string_move == square:
            i, j = square_to_index(move.to_square)
            available_moves_board[i][j] = 1
    if board.turn == chess.BLACK:
        from_move_board = np.flipud(from_move_board)
        available_moves_board = np.flipud(available_moves_board)
    return available_moves_board, from_move_board

def getChildMaxValue(node):
    max_children_value = float('-inf')
    for child_node in node.children.values():
        child_value = child_node.totalReward
        if child_value>max_children_value:
          max_children_value = child_value
    return max_children_value
import chess
import copy


import tensorflow as tf

interpreter_eval = tf.lite.Interpreter(model_content=model_eval_lite)
interpreter_eval.allocate_tensors()
input_details_eval = interpreter_eval.get_input_details()
output_details_eval = interpreter_eval.get_output_details()
input_index_eval = interpreter_eval.get_input_details()[0]["index"]

interpreter_piece = tf.lite.Interpreter(model_content=model_piece_lite)
interpreter_piece.allocate_tensors()
input_details_piece = interpreter_piece.get_input_details()
output_details_piece = interpreter_piece.get_output_details()
input_index_piece = interpreter_piece.get_input_details()[0]["index"]

interpreter_move = tf.lite.Interpreter(model_content=model_move_lite)
interpreter_move.allocate_tensors()
input_details_move = interpreter_move.get_input_details()
output_details_move = interpreter_move.get_output_details()
input_index_move = interpreter_move.get_input_details()[0]["index"]


def get_eval(splitted_dims_board):
    board3d = splitted_dims_board
    input_tensor = np.array(np.expand_dims(board3d, 0), dtype=np.float32)
    interpreter_eval.set_tensor(input_index_eval, input_tensor)
    interpreter_eval.invoke()
    output_details = output_details_eval[0]
    eval = interpreter_eval.get_tensor(output_details['index'])[0][0]
    eval = 1-eval
    return eval


def get_piece_board(board, splitted_dims_board,legal_moves):
    board3d = splitted_dims_board
    board3d = np.expand_dims(board3d, 0)
    board_clip = clip_board_pieces(board,legal_moves)
    if board.turn == chess.BLACK:
        black_turn = True
    else:
        black_turn = False
    input_tensor = np.array(board3d, dtype=np.float32)
    interpreter_piece.set_tensor(input_index_eval, input_tensor)
    interpreter_piece.invoke()
    output_details = output_details_piece[0]
    board = interpreter_piece.get_tensor(output_details['index'])[0]
    board = np.reshape(board, (8, 8))
    board = np.multiply(board, board_clip)
    sum = np.sum(board)
    if sum != 0:
        board = board/sum
    if black_turn == True:
        board = np.flipud(board)
    board = np.reshape(board, 64)
    from_move_distribution={}
    for i in range (len(chessboard)):
        if board[i]>0:
            piece_index = chessboard[i]
            piece_index = (int(piece_index[0]), int(piece_index[1]))
            from_square = str(index_squares[piece_index[1]]) + str(8-piece_index[0])
            from_move_distribution[from_square] = [board[i], None, board[i]]
    return from_move_distribution, board


def get_move_board(board, square, splitted_dims_board,legal_moves):
    if board.turn == chess.BLACK:
        black_turn = True
    else:
        black_turn = False
    available_moves_board, from_board = get_available_moves_board(board, square,legal_moves)
    board_added=splitted_dims_board
    board_added=list(board_added)
    board_added.append(available_moves_board)
    board_added.append(from_board)
    board_added = np.array(board_added)
    board_added = np.expand_dims(board_added, 0)
    input_tensor = np.array(board_added, dtype=np.float32)
    interpreter_move.set_tensor(input_index_eval, input_tensor)
    interpreter_move.invoke()
    output_details = output_details_move[0]
    board_move_prob = interpreter_move.get_tensor(output_details['index'])[0]
    board_move_prob = np.array(board_move_prob)
    board_move_prob = np.reshape(board_move_prob, (8, 8))
    board_move_prob = np.multiply(board_move_prob, available_moves_board)
    if black_turn == True:
        board_move_prob = np.flipud(board_move_prob)
        available_moves_board = np.flipud(available_moves_board)
    board_move_prob = np.reshape(board_move_prob, 64)
    available_moves_board = np.reshape(available_moves_board, 64)
    sum = np.sum(board_move_prob)
    if sum != 0:
        board_move_prob = board_move_prob / sum
    to_move_distribution = {}
    for i in range(64):
        if  available_moves_board[i] == 1:
            move_index = chessboard[i]
            move_index = (int(move_index[0]), int(move_index[1]))
            to_square = str(index_squares[move_index[1]]) + str(8 - move_index[0])
            to_move_distribution[to_square] = board_move_prob[i]
    return to_move_distribution, board_move_prob
def get_reward(board, turn):
    if board.result() == '1-0':
        reward = 0
    elif board.result() == '0-1':
        reward = 1
    else:
        reward = 0.5
    if turn == False:
        reward = 1-reward
    return reward

def NNPolicy(node):
    if not node.isTerminal:
        reward = get_eval(node.splitted_dims_board)
    else:
        turn = node.board.turn
        reward = get_reward(node.board, turn)
    return reward
def generate_move(board):
   split_board = split_dims(board, list(board.legal_moves))
   piece_probability_distribution = get_piece_board(board, split_board,
                                                    list(board.legal_moves))[1]
   piece_probability_distribution = np.reshape(piece_probability_distribution, 64)
   piece_index = np.random.choice(chessboard, p = piece_probability_distribution)
   piece_index= (int(piece_index[0]), int(piece_index[1]))
   from_square = str(index_squares[piece_index[1]]) + str(8 - piece_index[0])
   move_probability_distribution =get_move_board(board, from_square,  split_board,list(board.legal_moves))[1]
   move_probability_distribution = np.reshape(move_probability_distribution, 64)
   move_index = np.random.choice(chessboard, p = move_probability_distribution)
   move_index= (int(move_index[0]), int(move_index[1]))
   to_square = str(index_squares[move_index[1]]) + str(8 - move_index[0])
   move = from_square+to_square
   return(move)


def isTerminal(board):
    if board.legal_moves.count() == 0:
        return True
    else:
        return False
def MCMC(node, depth):
    if depth == 0:
        if not node.isTerminal:
            # pass the current state through CNN to get value of the position (% to win)
            reward = get_eval(node.splitted_dims_board)
        else:
            # get reward for the terminal node (0, 0.5, 1)
            turn = node.board.turn
            reward = get_reward(node.board, turn)
        return reward
    else:
        rewards = []
        turn = node.sideToMove
        for i in range (int(settings['number_of_simulations'])):
            state = node.board
            if not isTerminal(state):
                i = 0
                # until certain depth or terminal state is reached, do Markov Chain moves based on probability distribution given by CNN
                # each move CNN has to be 2 times (to get the piece and then the move), therefore it needs a lot of computation
                while not isTerminal(state) and i < depth:
                    action = generate_move(state)
                    move = chess.Move.from_uci(action)
                    state = copy.deepcopy(state)
                    state.push(move)
                    i += 1
                if isTerminal(state):
                    # if terminal state has been reached, get the reward
                    reward = get_reward(state, turn)
                else:
                    # pass the current state through CNN to get value of the position (% to win)
                    legal_moves = list(state.legal_moves)
                    reward = get_eval(split_dims(state, legal_moves))
                if state.turn != turn:
                    # swap the reward if the state was analysed from the opposite colour perspective
                    reward = 1-reward
            else:
                reward = get_reward(node.board, turn)
            #return reward
            rewards.append(reward)
        reward = statistics.mean(rewards)
        return reward
