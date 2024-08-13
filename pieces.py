import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
#type hinting

position_struct = tuple[int,int]
colour_list = []


#game constants
SIZE = 8
CELL_SIZE = 100

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

pieces_dictionary = {"pawn":1,"knight":2,"bishop":3,"rook":4,"queen":5,"king":6}

class Piece():
    """A chess piece."""
    def __init__(self, name, colour: int, position:position_struct,board):
        self.name = name
        self.colour = colour
        self.position = position
        self.vector_pos = pg.Vector2(position)
        self.srect = None
        

    def update(self):
        """Update the piece's position."""
        self.vector_pos = pg.Vector2(self.position)
        
    
    def move(self,new_position):
        """Move the piece to a new position."""
        self.position = new_position
        self.vector_pos = pg.Vector2(new_position)

    def capture(self, piece):
        """Capture another piece."""
        piece.move(None)
    
    def draw(self,screen) -> None:
        """Draw the piece on the screen."""
        path = self.name + str(self.colour) + ".png"
        image = pg.image.load(os.path.join(__location__,"Sprites",path)).convert_alpha()
        smol_image = pg.transform.scale(image,(CELL_SIZE-2,CELL_SIZE-2))
        srect = smol_image.get_rect(x=(self.vector_pos[1]*CELL_SIZE+1),y=(self.vector_pos[0]*CELL_SIZE+1))
        screen.blit(smol_image,srect) #draw the piece on the screen 
    
class Pawn(Piece):

    def __init__(self, colour:int, position:position_struct,board, moved = False,first_moved_double = False):
        super().__init__(name="pawn", colour=colour, position=position,board = board)
        self.moved = moved
        self.first_moved_double = first_moved_double
    
    def legal_moves(self,board,opposing_pieces):
        #Return a list of legal moves, opposing_pieces is it makes it easy to check for general legal moves without having to check for type
        legal_moves = []
        forward_pos = (self.position[0] + self.colour, self.position[1])
        left_pos = (self.position[0] + self.colour, self.position[1] + self.colour)
        right_pos = (self.position[0] + self.colour, self.position[1] - self.colour)
        left_side_pos = (self.position[0], self.position[1] - self.colour)
        right_side_pos = (self.position[0], self.position[1] + self.colour)
        pawn_double_move = (self.position[0] + (2 * self.colour), self.position[1])
        if board[forward_pos[0]][forward_pos[1]] == None:
            legal_moves.append(forward_pos)
        if left_pos[0] >= 0 and left_pos[1] >= 0 and left_pos[0] <= SIZE-1 and left_pos[1] <= SIZE-1:
            if board[left_pos[0]][left_pos[1]] != None: 
                if board[left_pos[0]][left_pos[1]].colour != self.colour: 
                    legal_moves.append(left_pos)
        if right_pos[0] >= 0 and right_pos[1] >= 0 and right_pos[0] <= SIZE-1 and right_pos[1] <= SIZE-1:
            if board[right_pos[0]][right_pos[1]] != None:
                if board[right_pos[0]][right_pos[1]].colour != self.colour:
                    legal_moves.append(right_pos)
        if not self.moved and board[forward_pos[0]][forward_pos[1]] == None:
            legal_moves.append(pawn_double_move)

        if left_side_pos[0] >= 0 and left_side_pos[1] >= 0 and left_side_pos[0] <= SIZE-1 and left_side_pos[1] <= SIZE-1:
            if self.first_moved_double and board[left_side_pos[0]][left_side_pos[1]] != None:
                if board[left_side_pos[0]][left_side_pos[1]].colour != self.colour and type(board[left_side_pos[0]][left_side_pos[1]]) == Pawn and board[left_side_pos[0]][left_side_pos[1]].first_moved_double:
                    legal_moves.append(left_pos)
        if right_side_pos[0] >= 0 and right_side_pos[1] >= 0 and right_side_pos[0] <= SIZE-1 and right_side_pos[1] <= SIZE-1:
            if self.first_moved_double and board[right_side_pos[0]][right_side_pos[1]] != None:
                if board[right_side_pos[0]][right_side_pos[1]].colour != self.colour and type(board[right_side_pos[0]][right_side_pos[1]]) == Pawn and board[right_side_pos[0]][right_side_pos[1]].first_moved_double:
                    legal_moves.append(right_pos)
            
        return legal_moves
    
    def attack_moves(self,board,opposing_pieces):
        attack_moves = []
        left_pos = (self.position[0] + self.colour, self.position[1] - self.colour)
        right_pos = (self.position[0] + self.colour, self.position[1] + self.colour)
        if left_pos[0] >= 0 and left_pos[1] >= 0 and left_pos[0] <= SIZE-1 and left_pos[1] <= SIZE-1:
            attack_moves.append(left_pos)
        if right_pos[0] >= 0 and right_pos[1] >= 0 and right_pos[0] <= SIZE-1 and right_pos[1] <= SIZE-1:   
            attack_moves.append(right_pos)
        return attack_moves
   
class King(Piece):

    def __init__(self, colour:int, position:position_struct,board,moved = False):
        super().__init__(name="king", colour=colour, position=position,board = board)
        self.moved = moved
    
    def legal_moves(self,board,opposing_pieces):
        """Return a list of legal moves."""
        legal_moves = []
        opposing_legal_moves = []
        for moves in [piece.attack_moves(board,opposing_pieces) for piece in opposing_pieces]:
            opposing_legal_moves.append(moves)
        for y in range(-1,2):
            for x in range(-1,2):
                if (y,x) == (0,0): continue 
                new_pos = (self.position[0] + y, self.position[1] + x)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
                if board[new_pos[0]][new_pos[1]] == None or board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
                if new_pos in opposing_legal_moves:
                    try:
                        legal_moves.remove(new_pos)
                    except: continue

        #castling
        if not self.moved:
            if board[self.position[0]][0] != None:
                if board[self.position[0]][0].colour == self.colour and board[self.position[0]][0].name == "rook" and not board[self.position[0]][0].moved and board[self.position[0]][1] == None and board[self.position[0]][2] == None and board[self.position[0]][3] == None:
                    legal_moves.append((self.position[0],2))
            if board[self.position[0]][7] != None:
                if board[self.position[0]][7].colour == self.colour and board[self.position[0]][7].name == "rook" and not board[self.position[0]][7].moved and board[self.position[0]][6] == None and board[self.position[0]][5] == None:
                    legal_moves.append((self.position[0],6))

        return legal_moves

    def attack_moves(self,board,opposing_pieces):
        attack_moves = []
        for y in range(-1,2):
            for x in range(-1,2):
                if y < 0 or x < 0 or y > SIZE-1 or x > SIZE-1: continue
                attack_moves.append((self.position[0] + y, self.position[1] + x))

        return attack_moves

class Queen(Piece):
    
    def __init__(self, colour:int, position:position_struct,board):
        super().__init__(name="queen", colour=colour, position=position,board = board)

    def legal_moves(self,board,opposing_pieces):
        """Return a list of legal moves."""
        initial_legal_moves = []
        legal_moves = []
        for y in range(-1,2):
            for x in range(-1,2):
                if (y,x) == (0,0): continue 
                new_pos = (self.position[0] + y, self.position[1] + x)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
                if board[new_pos[0]][new_pos[1]] == None:
                    initial_legal_moves.append(new_pos)
                    continue
                if board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
                    continue
        legal_moves.extend(initial_legal_moves)
        init_pos = self.position
        for move in initial_legal_moves:
            for i in range(2,SIZE):
                new_pos = (init_pos[0] + ((move[0] - init_pos[0])*i), init_pos[1] + ((move[1] - init_pos[1])*i))
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: break
                if board[new_pos[0]][new_pos[1]] == None:
                    legal_moves.append(new_pos)
                    continue
                if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
                    break
                if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]].colour == self.colour:
                    break
                continue
        return legal_moves
    
    def attack_moves(self,board,opposing_pieces):
        attack_moves = self.legal_moves(board,opposing_pieces)
        return attack_moves

class Bishop(Piece):

    def __init__(self, colour:int, position:position_struct,board):
        super().__init__(name="bishop", colour=colour, position=position,board = board)
    
    def legal_moves(self,board,opposing_pieces):
        """Return a list of legal moves."""
        initial_legal_moves = []
        legal_moves = []
        for y in range(-1,2):
            for x in range(-1,2):
                if (y,x) == (0,0): continue 
                if y == 0 or x == 0: continue
                new_pos = (self.position[0] + y, self.position[1] + x)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
                if board[new_pos[0]][new_pos[1]] == None:
                    initial_legal_moves.append(new_pos)
                    continue
                if board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
        legal_moves.extend(initial_legal_moves)
        init_pos = self.position
        for move in initial_legal_moves:
            for i in range(2,SIZE):
                new_pos = (init_pos[0] + (move[0] - init_pos[0])*i, init_pos[1] + (move[1] - init_pos[1])*i)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: break
                if board[new_pos[0]][new_pos[1]] == None:
                    legal_moves.append(new_pos)
                    continue
                if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
                    break
                if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]].colour == self.colour:
                    break
        return legal_moves

    def attack_moves(self,board,opposing_pieces):
        attack_moves = self.legal_moves(board,opposing_pieces)
        return attack_moves

class Rook(Piece):

    def __init__(self, colour:int, position:position_struct,board,moved = False):
        super().__init__(name="rook", colour=colour, position=position,board = board)
        self.moved = moved
    
    def legal_moves(self,board,opposing_pieces):
        """Return a list of legal moves."""
        initial_legal_moves = []
        legal_moves = []
        for y in range(-1,2):
            for x in range(-1,2):
                if (y,x) == (0,0): continue 
                if y != 0 and x != 0: continue
                new_pos = (self.position[0] + y, self.position[1] + x)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
                if board[new_pos[0]][new_pos[1]] == None:
                    initial_legal_moves.append(new_pos)
                    continue
                if board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
        legal_moves.extend(initial_legal_moves)
        init_pos = self.position
        for move in initial_legal_moves:
            for i in range(2,SIZE):
                new_pos = (init_pos[0] + (move[0] - init_pos[0])*i, init_pos[1] + (move[1] - init_pos[1])*i)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: break
                if board[new_pos[0]][new_pos[1]] == None:
                    legal_moves.append(new_pos)
                    continue
                if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
                    break
                if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]].colour == self.colour:
                    break
        return legal_moves
    
    def attack_moves(self,board,opposing_pieces):
        attack_moves = self.legal_moves(board,opposing_pieces)
        return attack_moves

class Knight(Piece):

    def __init__(self, colour:int, position:position_struct,board):
        super().__init__(name="knight", colour=colour, position=position,board = board)
    
    def legal_moves(self,board,opposing_pieces):
        """Return a list of legal moves."""
        init_pos = self.position
        legal_moves = []
        for y in range(-2,3):
            for x in range(-2,3):
                if (y,x) == (0,0): continue 
                if abs(y) == abs(x): continue
                if y == 0 or x == 0: continue
                new_pos = (self.position[0] + y, self.position[1] + x)
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
                if board[new_pos[0]][new_pos[1]] == None or board[new_pos[0]][new_pos[1]].colour != self.colour:
                    legal_moves.append(new_pos)
        return legal_moves
    
    def attack_moves(self,board,opposing_pieces):
        attack_moves = self.legal_moves(board,opposing_pieces)
        return attack_moves


def pawn_legal_moves(position,board,opposing_pieces,moved_pieces):
    #Return a list of legal moves, opposing_pieces is it makes it easy to check for general legal moves without having to check for type
    legal_moves = []
    moved = moved_pieces[position][0]
    first_moved_double = moved_pieces[position][1]
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    forward_pos = (position[0] + colour, position[1])
    left_pos = (position[0] + colour, position[1] + colour)
    right_pos = (position[0] + colour, position[1] - colour)
    left_side_pos = (position[0], position[1] - colour)
    right_side_pos = (position[0],position[1] + colour)
    pawn_double_move = (position[0] + (2 * colour), position[1])
    if board[forward_pos[0]][forward_pos[1]] == None:
        legal_moves.append(forward_pos)
    if left_pos[0] >= 0 and left_pos[1] >= 0 and left_pos[0] <= SIZE-1 and left_pos[1] <= SIZE-1:
        if board[left_pos[0]][left_pos[1]] != None: 
            if board[left_pos[0]][left_pos[1]]/abs(board[left_pos[0]][left_pos[1]]) != colour: 
                legal_moves.append(left_pos)
    if right_pos[0] >= 0 and right_pos[1] >= 0 and right_pos[0] <= SIZE-1 and right_pos[1] <= SIZE-1:
        if board[right_pos[0]][right_pos[1]] != None:
            if board[right_pos[0]][right_pos[1]]/abs(board[right_pos[0]][right_pos[1]]) != colour:
                legal_moves.append(right_pos)
    if not moved and board[forward_pos[0]][forward_pos[1]] == None:
        legal_moves.append(pawn_double_move)

    if left_side_pos[0] >= 0 and left_side_pos[1] >= 0 and left_side_pos[0] <= SIZE-1 and left_side_pos[1] <= SIZE-1:
        if first_moved_double and board[left_side_pos[0]][left_side_pos[1]] != None:
            if board[left_side_pos[0]][left_side_pos[1]]/abs(board[left_side_pos[0]][left_side_pos[1]]) != colour and type(board[left_side_pos[0]][left_side_pos[1]]) == Pawn and moved_pieces[(left_side_pos[0],left_side_pos[1])][1]:
                legal_moves.append(left_pos)
    if right_side_pos[0] >= 0 and right_side_pos[1] >= 0 and right_side_pos[0] <= SIZE-1 and right_side_pos[1] <= SIZE-1:
        if first_moved_double and board[right_side_pos[0]][right_side_pos[1]] != None:
            if board[right_side_pos[0]][right_side_pos[1]]/abs(board[right_side_pos[0]][right_side_pos[1]]) != colour and type(board[right_side_pos[0]][right_side_pos[1]]) == Pawn and moved_pieces[(right_side_pos[0],right_side_pos[1])][1]:
                legal_moves.append(right_pos)
        
    return legal_moves

def pawn_attack_moves(position,board,opposing_pieces,moved_pieces):
    attack_moves = []
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    left_pos = (position[0] + colour, position[1] - colour)
    right_pos = (position[0] + colour, position[1] + colour)
    if left_pos[0] >= 0 and left_pos[1] >= 0 and left_pos[0] <= SIZE-1 and left_pos[1] <= SIZE-1:
        attack_moves.append(left_pos)
    if right_pos[0] >= 0 and right_pos[1] >= 0 and right_pos[0] <= SIZE-1 and right_pos[1] <= SIZE-1:   
        attack_moves.append(right_pos)
    return attack_moves

def king_legal_moves(position,board,opposing_pieces,moved_pieces):
    """Return a list of legal moves."""
    legal_moves = []
    opposing_legal_moves = []
    moved = moved = moved_pieces[position][0]
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    for moves in [piece.attack_moves(board,opposing_pieces) for piece in opposing_pieces]:
        opposing_legal_moves.append(moves)
    for y in range(-1,2):
        for x in range(-1,2):
            if (y,x) == (0,0): continue 
            new_pos = (position[0] + y, position[1] + x)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
            if board[new_pos[0]][new_pos[1]] == None or board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
            if new_pos in opposing_legal_moves:
                try:
                    legal_moves.remove(new_pos)
                except: continue
    #castling
    if not moved:
        if board[position[0]][0] != None:
            if board[position[0]][0]/abs(board[position[0]][0]) == colour and board[position[0]][0] == pieces_dictionary["rook"] and not moved_pieces[(position[0],[0])][0] and board[position[0]][1] == None and board[position[0]][2] == None and board[position[0]][3] == None:
                legal_moves.append((position[0],2))
        if board[position[0]][7] != None:
            if board[position[0]][7]/abs(board[position[0]][7]) == colour and board[position[0]][7] == pieces_dictionary["rook"] and not moved_pieces[([position[0]],[7])][0] and board[position[0]][6] == None and board[position[0]][5] == None:
                legal_moves.append((position[0],6))

        return legal_moves

def king_attack_moves(position,board,opposing_pieces,moved_pieces):
    attack_moves = []
    for y in range(-1,2):
        for x in range(-1,2):
            if y < 0 or x < 0 or y > SIZE-1 or x > SIZE-1: continue
            attack_moves.append((position[0] + y, position[1] + x))

    return attack_moves

def queen_legal_moves(position,board,opposing_pieces,moved_pieces):
    """Return a list of legal moves."""
    initial_legal_moves = []
    legal_moves = []
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    for y in range(-1,2):
        for x in range(-1,2):
            if (y,x) == (0,0): continue 
            new_pos = (position[0] + y, position[1] + x)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
            if board[new_pos[0]][new_pos[1]] == None:
                initial_legal_moves.append(new_pos)
                continue
            if board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
                continue
    legal_moves.extend(initial_legal_moves)
    init_pos = position
    for move in initial_legal_moves:
        for i in range(2,SIZE):
            new_pos = (init_pos[0] + ((move[0] - init_pos[0])*i), init_pos[1] + ((move[1] - init_pos[1])*i))
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: break
            if board[new_pos[0]][new_pos[1]] == None:
                legal_moves.append(new_pos)
                continue
            if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
                break
            if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) == colour:
                break
            continue
    return legal_moves

def bishop_legal_moves(position,board,opposing_pieces,moved_pieces):
    """Return a list of legal moves."""
    initial_legal_moves = []
    legal_moves = []
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    for y in range(-1,2):
        for x in range(-1,2):
            if (y,x) == (0,0): continue 
            if y == 0 or x == 0: continue
            new_pos = (position[0] + y, position[1] + x)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
            if board[new_pos[0]][new_pos[1]] == None:
                initial_legal_moves.append(new_pos)
                continue
            if board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
    legal_moves.extend(initial_legal_moves)
    init_pos = position
    for move in initial_legal_moves:
        for i in range(2,SIZE):
            new_pos = (init_pos[0] + (move[0] - init_pos[0])*i, init_pos[1] + (move[1] - init_pos[1])*i)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: break
            if board[new_pos[0]][new_pos[1]] == None:
                legal_moves.append(new_pos)
                continue
            if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
                break
            if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) == colour:
                break
    return legal_moves

def rook_legal_moves(position,board,opposing_pieces,moved_pieces):
    """Return a list of legal moves."""
    initial_legal_moves = []
    legal_moves = []
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    for y in range(-1,2):
        for x in range(-1,2):
            if (y,x) == (0,0): continue 
            if y != 0 and x != 0: continue
            new_pos = (position[0] + y, position[1] + x)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
            if board[new_pos[0]][new_pos[1]] == None:
                initial_legal_moves.append(new_pos)
                continue
            if board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
    legal_moves.extend(initial_legal_moves)
    init_pos = position
    for move in initial_legal_moves:
        for i in range(2,SIZE):
            new_pos = (init_pos[0] + (move[0] - init_pos[0])*i, init_pos[1] + (move[1] - init_pos[1])*i)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: break
            if board[new_pos[0]][new_pos[1]] == None:
                legal_moves.append(new_pos)
                continue
            if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
                break
            if board[new_pos[0]][new_pos[1]] != None and board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) == colour:
                break
    return legal_moves

def knight_legal_moves(position,board,opposing_pieces,moved_pieces):
    """Return a list of legal moves."""
    legal_moves = []
    colour = board[position[0]][position[1]]/abs(board[position[0]][position[1]])
    for y in range(-2,3):
        for x in range(-2,3):
            if (y,x) == (0,0): continue 
            if abs(y) == abs(x): continue
            if y == 0 or x == 0: continue
            new_pos = (position[0] + y, position[1] + x)
            if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > SIZE-1 or new_pos[1] > SIZE-1: continue
            if board[new_pos[0]][new_pos[1]] == None or board[new_pos[0]][new_pos[1]]/abs(board[new_pos[0]][new_pos[1]]) != colour:
                legal_moves.append(new_pos)
    return legal_moves

legal_move_functions = [pawn_attack_moves,knight_legal_moves,bishop_legal_moves,rook_legal_moves,queen_legal_moves,king_legal_moves]
attack_move_functions = [pawn_legal_moves,knight_legal_moves,bishop_legal_moves,rook_legal_moves,queen_legal_moves,king_attack_moves]