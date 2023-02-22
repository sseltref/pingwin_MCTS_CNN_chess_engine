import chess
import stockfish
import random
import numpy as np
import multiprocessing
import math



stockfish = stockfish.Stockfish(path=r"")
stockfish.set_depth(10)



'''def split_dims(board):
  board3d = np.zeros((14, 8, 8), dtype=np.int8)

  for piece in chess.PIECE_TYPES:
    for square in board.pieces(piece, chess.WHITE):
      idx = np.unravel_index(square, (8, 8))
      board3d[piece - 1][7 - idx[0]][idx[1]] = 1
    for square in board.pieces(piece, chess.BLACK):
      idx = np.unravel_index(square, (8, 8))
      board3d[piece + 5][7 - idx[0]][idx[1]] = 1


  aux = board.turn
  board.turn = chess.WHITE
  for move in board.legal_moves:
      i, j = square_to_index(move.to_square)
      board3d[12][i][j] = 1
  board.turn = chess.BLACK
  for move in board.legal_moves:
      i, j = square_to_index(move.to_square)
      board3d[13][i][j] = 1
  board.turn = aux

  return board3d'''

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


def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]


def split_dims(board):
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
    board.turn = chess.WHITE
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[6][i][j] = v
    board.turn = chess.BLACK
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[7][i][j] = -v
    board.turn = aux
    if v == -1:
        for i in range(len(board3d)):
            flipped_board = np.flipud(board3d[i])
            board3d[i] = flipped_board
    return board3d



def random_board(max_depth=200):
  board = chess.Board()
  depth = random.randrange(1, max_depth)
  for _ in range(depth):
    all_moves = list(board.legal_moves)
    random_move = random.choice(all_moves)
    board.push(random_move)
    if board.is_game_over():
        board.pop()
        break
  return board


def stockfish_eval(board):
        board_fen = board.fen()
        stockfish.set_fen_position(board_fen)
        eval = stockfish.get_evaluation()
        if eval['type'] == 'mate':
                eval=eval['value']
                if eval>0:
                    eval = 1000
                if eval<0:
                    eval = -1000
        else:
            eval = eval["value"]
        piece_move = stockfish.get_best_move()
        to_square = piece_move[2:4]
        to_move_board = np.zeros((8, 8), dtype=np.int8)
        piece_idx_1 = 8 - int(to_square[1])
        piece_idx_2 = squares_index[to_square[0]]
        to_move_board[piece_idx_1][piece_idx_2] = 1
        from_square = piece_move[0:2]
        from_move_board = np.zeros((8, 8), dtype=np.int8)
        piece_idx_1 = 8 - int(from_square[1])
        piece_idx_2 = squares_index[from_square[0]]
        from_move_board[piece_idx_1][piece_idx_2] = 1
        available_moves_board = np.zeros((8, 8), dtype=np.int8)
        for move in board.legal_moves:
            string_move = str(move)[0:2]
            if string_move == piece_move[0:2]:
                i, j = square_to_index(move.to_square)
                available_moves_board[i][j] = 1
        if board.turn == chess.BLACK:
            to_move_board = np.flipud(to_move_board)
            from_move_board = np.flipud(from_move_board)
            available_moves_board = np.flipud(available_moves_board)
        if board.turn == chess.WHITE:
            v = 1
        else:
            v = -1
        eval=eval*v
        return board,eval, to_move_board, from_move_board, available_moves_board

def generate_dataset():
    board_list = []
    eval_list = []
    eval_sigmoid_list = []
    to_move_board_list=[]
    from_move_board_list=[]
    available_moves_board_list=[]
    i = 1
    for _ in range(10000):
        board = random_board()
        board, eval, to_move_board, from_move_board, available_moves_board = stockfish_eval(board)
        eval = eval/100
        board = split_dims(board)
        board_list.append(board)
        eval_list.append(eval)
        to_move_board_list.append(to_move_board)
        from_move_board_list.append(from_move_board)
        available_moves_board_list.append(available_moves_board)
        eval_sigmoid_list.append(1 / (1 + math.exp(-eval)))
        print(i)
        i = i+1

    return np.array(board_list), np.array(eval_list), np.array(eval_sigmoid_list), np.array(to_move_board_list), np.array(from_move_board_list), np.array(available_moves_board_list)

def save_dataset(depth, thread):
    k=1
    while k<6:
        f=1
        while f<11:
            board, eval, eval_sigmoid, to_move_board, from_move_board, available_moves_board = generate_dataset()
            data = {'board': board,
                    'eval': eval,
                    'eval_sigmoid': eval_sigmoid,
                    'to_move_board': to_move_board,
                    'from_move_board': from_move_board,
                    'available_moves_board': available_moves_board}
            np.savez("available_dataset_depth_{}_thread_{}_batch_{}_{}.npz".format(depth, thread, k,f), board=data['board'], eval=data['eval'], eval_sigmoid=data['eval_sigmoid'], to_move_board=data['to_move_board'], from_move_board=data['from_move_board'],available_moves_board=data['available_moves_board'])
            f+=1
        k+=1
def go():
    i = 10
    while i ==10:
        stockfish.set_depth(i)
        print("depth set to: ", i)
        processes=[]
        j=1
        while j <11 :
            t = multiprocessing.Process(target=save_dataset, args=(i, j))
            processes.append(t)
            t.start()
            print("process{}started".format(j))
            j = j + 1

        for thread in processes:
            thread.join()
        i = i+1
def profile():
    board = chess.Board()
    board = split_dims(board)
    print(board)
import cProfile
if __name__ == '__main__':
    cProfile.run('profile()')
    #go()



