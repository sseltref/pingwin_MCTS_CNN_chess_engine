import numpy as np
data = np.load("available_dataset_depth_10_thread_1_batch_1_1.npz")
board = data['board'][0:1]
eval = data['eval'][0:1]
eval_sigmoid = data['eval'][0:1]
eval_sigmoid = eval_sigmoid * 100
eval_sigmoid = (50+50*(2/(1+ np.exp(-0.00368208*eval_sigmoid)) -1))/100
to_move_board = data['to_move_board'][0:1]
from_move_board = data['from_move_board'][0:1]
available_moves_board = data['available_moves_board'][0:1]
i = 1
while i < 11:
    j=1
    while j < 6:
        k=1
        while k <11:
            data = np.load("available_dataset_depth_10_thread_{}_batch_{}_{}.npz".format(i, j, k))
            board = np.concatenate((board, data['board']))
            eval = np.concatenate((eval, data['eval']))
            new_eval=data['eval']
            new_eval = new_eval * 100
            new_eval = (50 + 50 * (2 / (1 + np.exp(-0.00368208 * new_eval)) - 1)) / 100
            eval_sigmoid = np.concatenate((eval_sigmoid, new_eval))
            to_move_board = np.concatenate((to_move_board, data['to_move_board']))
            from_move_board = np.concatenate((from_move_board, data['from_move_board']))
            available_moves_board = np.concatenate((available_moves_board, data['available_moves_board']))
            k+=1
            print(i, j, k)
        j+=1
    i+=1
np.savez("availavle_dataset_merged", board=board, eval=eval, eval_sigmoid=eval_sigmoid, to_move_board=to_move_board, from_move_board=from_move_board,available_moves_board=available_moves_board)