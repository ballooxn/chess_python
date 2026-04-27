#offsets
BISHOP_MOVES = [[i, j] for i in range(-7, 8) if i != 0 for j in [i, -i]]
ROOK_MOVES = [[i, 0] for i in range(-7,8) if i != 0] + [[0, j] for j in range(-7,8) if j != 0]
PIECE_MOVES = {
    'p': {
        'w': [[-1,1], [-1,0], [-1,-1], [-2, 0]],
        'b': [[1,-1], [1,0], [1,1], [2, 0]]
    },
    'k': [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]],
    'n': [[2, 1], [1, 2], [-2, 1], [1, -2], [-1, 2], [2, -1], [-2, -1], [-1, -2]],
    'b': BISHOP_MOVES,
    'r': ROOK_MOVES,
    'q': BISHOP_MOVES + ROOK_MOVES
}

class Piece:
    def __init__(self, typee, color, times_moved=0):
        self.type = typee # two e's to bypass the 'type' python thing
        self.color = color
        self.times_moved = times_moved

    def to_dict(self):
        return {
            'type': self.type,
            'color': self.color
        }
    
    @classmethod
    def get_all_possible_moves(cls, ptype, color=None):
        if ptype == "p":
            return PIECE_MOVES['p'][color]
        else:
            return PIECE_MOVES[ptype]

    #Handle special pawn moves (diagonal, en passeant, two moves, etc.)
    def legal_pawn_move(cls, current_pos, end_pos, player, board):
        move_y = end_pos[0] - current_pos[0]
        move_x = end_pos[1] - current_pos[1]

        target_piece = board[end_pos[0]][end_pos[1]]
        #Pawns cannot move capture forward
        if move_x == 0 and target_piece != "_":
            return False

        # En passant: Capturing pawn must have advanced 3 squares, captured pawn must have advanced two squares in one move.
        if (move_y != 0 and move_x != 0) and target_piece == '_': #Moving diagonally to en passant and moving to empty square
            side_pawn = board[current_pos[0]][current_pos[1] + move_x]
            if side_pawn != '_' and side_pawn.color != player:
                # the captruing pawn must have advanced three squares forward
                valid_capturing_row = 3 if player == 'w' else 4
                # The captured pawn must have moved 2 squares 1 time
                if current_pos[0] == valid_capturing_row and side_pawn.times_moved == 1:
                    return 'enpassant'
                else:
                    return False
            else:
                return False

         # Pawns cannot move diagonally unless capturing, and pawns can only move two squares on their first move.
        if player == "w":
            if [move_y, move_x] == [-2, 0] and current_pos[0] != 6:
                return False
            elif ([move_y, move_x] == [-1, 1] or [move_y, move_x] == [-1, -1]) and target_piece  == "_":
                return False
        elif player == "b":
            if [move_y, move_x] == [2, 0] and current_pos[0] != 1:
                return False
            elif move_x != 0 and target_piece == "_":
                return False
            
            
        return True