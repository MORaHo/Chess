from pieces import Knight,Queen,King,Bishop,Rook,Pawn
import numpy as np


board = [[None] for i in range(64)]
board = np.array(board).reshape(8,8)

knight = Knight(-1,(7,4),board)
board[7][4] = knight
king = King(-1,(0,0),board)
board[0][0] = king
print(knight.legal_moves(board,[]))
print(board)