
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import numpy
import pygame as pg
from pieces import King,Queen,Bishop,Knight,Rook,Pawn,Piece

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#game start constants
SIZE = 8
WHITE = -1
BLACK = 1

#board variables
black_pieces = []
white_pieces = []
king_poss = {BLACK:(0,0),WHITE:(0,1)}
clicked_piece = None
piece_legal_moves = []
en_passant_has_happened = False
en_passanted_pawn = None

#pygame variables

CELL_SIZE = 100
screen_sizes = (CELL_SIZE * SIZE,CELL_SIZE * SIZE)
baige = (235,227,211)
green = (118,150,86)
colour_list = [baige,green]
player_turn = WHITE
clicks = 0
lost = False
first_click = True

#form board
empty_work_board = []
def form_board():
    for a in range(SIZE):
        for b in range(SIZE):
            empty_work_board.append([None])
    work_board = numpy.array(empty_work_board,dtype=object).reshape(SIZE,SIZE)
    for i in range(0,SIZE):
        work_board[1][i] = Pawn(BLACK,(1,i),work_board)
        work_board[SIZE-2][i] = Pawn(WHITE,(SIZE-2,i),work_board)
    work_board[0][0] = Rook(BLACK,(0,0),work_board)
    work_board[SIZE-1][0] = Rook(WHITE,(SIZE-1,0),work_board)
    work_board[0][1] = Knight(BLACK,(0,1),work_board)
    work_board[SIZE-1][1] = Knight(WHITE,(SIZE-1,1),work_board)
    work_board[0][2] = Bishop(BLACK,(0,2),work_board)
    work_board[SIZE-1][2] = Bishop(WHITE,(SIZE-1,2),work_board)
    work_board[0][3] = Queen(BLACK,(0,3),work_board)
    work_board[SIZE-1][3] = Queen(WHITE,(SIZE-1,3),work_board)
    work_board[0][4] = King(BLACK,(0,4),work_board)
    work_board[SIZE-1][4] = King(WHITE,(SIZE-1,4),work_board)
    work_board[0][5] = Bishop(BLACK,(0,5),work_board)
    work_board[SIZE-1][5] = Bishop(WHITE,(SIZE-1,5),work_board)
    work_board[0][6] = Knight(BLACK,(0,6),work_board)
    work_board[SIZE-1][6] = Knight(WHITE,(SIZE-1,6),work_board)
    work_board[0][7] = Rook(BLACK,(0,7),work_board)
    work_board[SIZE-1][7] = Rook(WHITE,(SIZE-1,7),work_board)

    return work_board

board = form_board()
black_pieces = [piece for piece in board[3-(3*BLACK)]] + [piece for piece in board[4-(3*BLACK)]]
white_pieces = [piece for piece in board[3-(3*WHITE)]] + [piece for piece in board[4-(3*WHITE)]]
king_poss[BLACK] = board[0][4]
king_poss[WHITE] = board[7][4]
pieces_list = black_pieces + white_pieces
pieces = {BLACK:black_pieces,WHITE:white_pieces}

#pygame initialization
pg.init()
CLOCK = pg.time.Clock()
screen = pg.display.set_mode((SIZE*CELL_SIZE,SIZE*CELL_SIZE),0,32)
pg.display.set_caption("Chess")
screen.fill(baige)

def draw_board():
    screen.fill(baige)
    for x in range(0, 8, 2):
        for y in range(0, 8, 2):
            pg.draw.rect(screen,colour_list[1], (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pg.draw.rect(screen,colour_list[1], ((x+1)*CELL_SIZE, (y+1)*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for piece in pieces_list:
        piece.draw(screen)

    pg.display.update()

draw_board()

def clear_recurring_variables():
    global clicked_piece,piece_legal_moves,first_click,first_click_coords
    clicked_piece = None
    piece_legal_moves = []
    first_click = True
    first_click_coords = []

def check_check(board,player_turn):
    for piece in pieces[-player_turn]:
        if king_poss[player_turn].position in piece.attack_moves(board,pieces[player_turn]):
            return True
    return False

def check_checkmate(board,player_turn):

    non_check_positions = []
    for piece in pieces[player_turn]:
        for move in piece.legal_moves(board,pieces[-player_turn]):
            original_position = piece.position
            board[move[0]][move[1]] = piece
            board[original_position[0]][original_position[1]] = None
            piece.move(move)
            if not check_check(board,player_turn):
                non_check_positions.append(move)
            board[move[0]][move[1]] = None
            board[original_position[0]][original_position[1]] = piece
            piece.move(original_position)

    if len(non_check_positions) == 0:
        return True
    else:
        return False


while not lost:


    for event in pg.event.get():

        if event.type == pg.QUIT:
            lost = True
        
        if event.type == pg.MOUSEBUTTONDOWN:   

            mouse_pos = pg.mouse.get_pos()
            matrix_indices = [int(mouse_pos[1]//CELL_SIZE),int(mouse_pos[0]//CELL_SIZE)]

            if board[matrix_indices[0]][matrix_indices[1]] != None and first_click:

                if board[matrix_indices[0]][matrix_indices[1]].colour == player_turn:

                    clicked_piece = board[matrix_indices[0]][matrix_indices[1]]
                    piece_legal_moves = board[matrix_indices[0]][matrix_indices[1]].legal_moves(board,pieces[-player_turn])
                    first_click = False
                    first_click_coords = matrix_indices

            elif not first_click:

                old_pos = clicked_piece.position 
                move_to_position_tuple = (matrix_indices[0],matrix_indices[1])

                if move_to_position_tuple not in piece_legal_moves:

                    clicked_piece = None
                    piece_legal_moves = []
                    first_click = True

                elif (matrix_indices[0],matrix_indices[1]) in piece_legal_moves:
                        
                        

                    if type(clicked_piece) == Pawn or type(clicked_piece) == Rook or type(clicked_piece) == King:

                        clicked_piece.moved = True

                        if type(clicked_piece) == Pawn and abs(matrix_indices[0] - old_pos[0]) == 2:
                            clicked_piece.first_moved_double = True

                        if type(clicked_piece) == Rook:
                            clicked_piece.castle_position = []

                    if board[matrix_indices[0]][matrix_indices[1]] != None:
                            
                        opposing_pieces = pieces[-player_turn]
                        removing_board_position = board[matrix_indices[0]][matrix_indices[1]]
                        opposing_pieces.remove(removing_board_position)
                        pieces_list.remove(removing_board_position)
                        board[matrix_indices[0]][matrix_indices[1]] = None
                        board[first_click_coords[0]][first_click_coords[1]] = None

                        clicked_piece.move(move_to_position_tuple)
                        board[matrix_indices[0]][matrix_indices[1]] = clicked_piece

                        #check if the move a causes a check if so then undo the move
                        if check_check(board,player_turn): #if it causes check
                                
                                board[first_click_coords[0]][first_click_coords[1]] = clicked_piece
                                board[matrix_indices[0]][matrix_indices[1]] = removing_board_position
                                opposing_pieces.append(removing_board_position)
                                pieces_list.append(removing_board_position)
                                if check_checkmate(board,player_turn):
                                    print("checkmate")
                                    lost = True
                                    continue
                                clear_recurring_variables()
                                continue
                        
                        #promotion
                        if type(clicked_piece) == Pawn and (matrix_indices[0] == 0 or matrix_indices[0] == 7):
                            board[matrix_indices[0]][matrix_indices[1]] = None
                            board[matrix_indices[0]][matrix_indices[1]] = Queen(player_turn,(matrix_indices[0],matrix_indices[1]),board)
                            pieces[player_turn].append(board[matrix_indices[0]][matrix_indices[1]])
                            pieces_list.append(board[matrix_indices[0]][matrix_indices[1]])
                            pieces[player_turn].remove(clicked_piece)
                            pieces_list.remove(clicked_piece)

                        clear_recurring_variables()
                        draw_board()
                        player_turn *= -1
                        continue

                    else:
                        
                        clicked_piece.move(move_to_position_tuple)
                        board[first_click_coords[0]][first_click_coords[1]] = None
                        board[matrix_indices[0]][matrix_indices[1]] = clicked_piece

                        if type(clicked_piece) == Pawn:
                            if abs(matrix_indices[0] - old_pos[0]) == 1 and abs(matrix_indices[1] - old_pos[1]) == 1:
                                en_passant_has_happened = True
                                en_passanted_pawn = board[matrix_indices[0]-player_turn][matrix_indices[1]]
                                board[matrix_indices[0]-player_turn][matrix_indices[1]] = None
                                pieces[-player_turn].remove(en_passanted_pawn)
                                pieces_list.remove(en_passanted_pawn)
                                

                        if check_check(board,player_turn):
                            print("check")
                            print(king_poss[player_turn].legal_moves(board,pieces[-player_turn]))
                            board[first_click_coords[0]][first_click_coords[1]] = clicked_piece
                            board[matrix_indices[0]][matrix_indices[1]] = None
                            clicked_piece.move(old_pos)
                            if en_passant_has_happened:
                                board[matrix_indices[0]-player_turn][matrix_indices[1]] = en_passanted_pawn
                                pieces[-player_turn].append(en_passanted_pawn)
                                pieces_list.append(en_passanted_pawn)
                                en_passant_has_happened = False
                                en_passanted_pawn = None
                                continue
                            if check_checkmate(board,player_turn):
                                print("checkmate")
                                lost = True
                                continue 
                            continue
                                        
                        
                        #castling, assumes that the position is legal since it has already been checked
                        if type(clicked_piece) == King and abs(matrix_indices[1] - old_pos[1]) == 2:
                            difference = matrix_indices[1] - old_pos[1]
                            multiplies = difference//abs(difference)
                            if multiplies == 1:
                                rook = board[matrix_indices[0]][7]
                            else:
                                rook = board[matrix_indices[0]][0]
                            rook.move((matrix_indices[0],4+multiplies))
                            board[matrix_indices[0]][4+multiplies] = rook
                            board[matrix_indices[0]][4+multiplies] = None

                        #promotion
                        if type(clicked_piece) == Pawn and (matrix_indices[0] == 0 or matrix_indices[0] == 7):
                            print('promotion')
                            board[matrix_indices[0]][matrix_indices[1]] = None
                            board[matrix_indices[0]][matrix_indices[1]] = Queen(player_turn,(matrix_indices[0],matrix_indices[1]),board)
                            pieces[player_turn].append(board[matrix_indices[0]][matrix_indices[1]])
                            pieces_list.append(board[matrix_indices[0]][matrix_indices[1]])
                            pieces[player_turn].remove(clicked_piece)
                            pieces_list.remove(clicked_piece)

                        clear_recurring_variables()
                        draw_board()
                        player_turn *= -1

