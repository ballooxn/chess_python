from .piece import Piece

class Board:
    def __init__(self):
        back_rank_types = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']

        black_back_rank = [Piece(p, 'b') for p in back_rank_types]
        black_pawns = [Piece('p', 'b') for _ in range(8)]
        empty_rows = [['_' for _ in range(8)] for _ in range(4)]
        white_pawns = [Piece('p', 'w') for _ in range(8)]
        white_back_rank = [Piece(p, 'w') for p in back_rank_types]

        # Combine all ranks into the board
        self.board = [black_back_rank] + [black_pawns] + empty_rows + [white_pawns] + [white_back_rank]

        self.white_piece_locations = [[7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7],  
        [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7]] 
        self.black_piece_locations = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7],
        [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7]]
    
    def get_locations(self, player):
        return self.black_piece_locations if player == "b" else self.white_piece_locations
    
    def move_piece(self, move, player):
        piece_at_target = self.board[move["end_pos"][0]][move["end_pos"][1]]
        current_piece = self.board[move["start_pos"][0]][move["start_pos"][1]]
        other_player = 'w' if player == 'b' else 'b'

        # Detect en passant and remove side pawn if it is.
        if current_piece.type == "p" and move["start_pos"][1] != move["end_pos"][1] and piece_at_target == "_":
            side_pawn_location = [move["start_pos"][0], move["end_pos"][1]]
            opponent_list = self.get_locations(other_player)
            opponent_list.remove(side_pawn_location)
            self.board[side_pawn_location[0]][side_pawn_location[1]] = "_"

        if piece_at_target != "_":
            opponent_list = self.get_locations(other_player)
            opponent_list.remove(move["end_pos"])

        player_list = self.get_locations(player)

        player_list.remove(move["start_pos"])
        player_list.append(move["end_pos"])

        self.board[move["start_pos"][0]][move["start_pos"][1]] = "_"
        self.board[move["end_pos"][0]][move["end_pos"][1]] = current_piece
    
    def reverse_simulated_move(self, move, player, piece_at_target):
        current_piece = self.board[move["end_pos"][0]][move["end_pos"][1]]
        self.board[move["end_pos"][0]][move["end_pos"][1]] = piece_at_target
        self.board[move["start_pos"][0]][move["start_pos"][1]] = current_piece
        other_player = 'w' if player == 'b' else 'b'

        #  detect en passant and restore if it is.
        if current_piece.type == "p" and move["start_pos"][1] != move["end_pos"][1] and piece_at_target == "_":
            side_pawn_location = [move["start_pos"][0], move["end_pos"][1]]
            opponent_list = self.get_locations(other_player)
            opponent_list.append(side_pawn_location)
            self.board[side_pawn_location[0]][side_pawn_location[1]] = Piece('p', other_player, 1)

        if piece_at_target != "_":
            opponent_list = self.get_locations(other_player)
            opponent_list.append(move["end_pos"])
        player_list = self.get_locations(player)

        player_list.append(move["start_pos"])
        player_list.remove(move["end_pos"])

    def valid_move(self, move, player):
        target = self.board[move['end_pos'][0]][move['end_pos'][1]]

        if target != "_" and target.color == player:
            return False # Cannot capture own piece.
        
        if self.can_move(move, player):
                self.move_piece(move, player)
                is_safe = not self.in_check(player)
                self.reverse_simulated_move(move, player, target)

                if is_safe:
                    return True
        return False
    
    def in_check(self, player):
        #Find the king
        king_position = None
        location_list = self.get_locations(player)

        for location in location_list:
                square = self.board[location[0]][location[1]]
                if square != '_' and square.color == player and square.type == "k":
                    king_position = location

        #Check every opponent piece to see if they can move to king (sort of like valid_move())
        opponent = "b" if player == "w" else "w"
        opponent_list = self.get_locations(opponent)

        for start_pos in opponent_list:
            # Create a fake move 
            move = {
                'start_pos': start_pos,
                'end_pos': king_position
            }
            if self.can_move(move, opponent):
                return True
        return False
    
    def in_checkmate(self, player):
        if not self.in_check(player):
            return False
        
        return not self.has_legal_moves(player)
    
    def in_stalemate(self, player):
        if self.in_check(player):
            return False
        print("Checking for stalemate.")
        return not self.has_legal_moves(player)
    
    # Used by checkmate and stalemate check
    def has_legal_moves(self, player):
        # Check each piece to see if they can make a move to where king is NOT in check
        location_list = self.get_locations(player)

        for location in location_list:
            piece = self.board[location[0]][location[1]]
            if piece != "_" and piece.color == player:
                moves = Piece.get_all_possible_moves(piece.type, piece.color)
                for move in moves:
                    target_row = location[0] + move[0]
                    target_column = location[1] + move[1]
                    target_move = {
                        'start_pos': location,
                        'end_pos': [target_row, target_column]
                    }

                    if 0 <= target_row <= 7 and 0 <= target_column <= 7:
                        target_square = self.board[target_row][target_column]
                        if target_square != "_" and target_square.color == player:
                            continue

                        if self.can_move(target_move, player):
                            piece_at_target = self.board[target_row][target_column]

                            self.move_piece(target_move, player)
                            is_safe = not self.in_check(player)
                            self.reverse_simulated_move(target_move, player, piece_at_target)

                            if is_safe:
                                print("Designated as safe")
                                return True
        return False

    def can_move(self, move, player):
        piece = self.board[move['start_pos'][0]][move['start_pos'][1]]
        moves = Piece.get_all_possible_moves(piece.type, player)

        move_y = move["end_pos"][0] - move["start_pos"][0]
        move_x = move["end_pos"][1] - move["start_pos"][1]

        if [move_y, move_x] in moves:
            if piece.type == "n":
                return True
            if piece.type == "p" and not Piece.legal_pawn_move(Piece, [move["start_pos"][0], move["start_pos"][1]], [move["end_pos"][0], move["end_pos"][1]], player, self.board):
                return False

            #Check for collisions.
            step_row = int(move_y / abs(move_y)) if move_y != 0 else 0
            step_column = int(move_x / abs(move_x)) if move_x != 0 else 0

            temp_row = move["start_pos"][0] + step_row
            temp_column = move["start_pos"][1] + step_column

            while temp_row != move["end_pos"][0] or temp_column != move["end_pos"][1]:

                if self.board[temp_row][temp_column] != "_":
                    return False
                
                temp_row += step_row
                temp_column += step_column
            return True
        
    def get_legal_moves(self, piece, pos):

        moves = piece.get_all_possible_moves()

        legal_moves = []

        for move in moves:
            move_dict = {
            "start_pos": [pos[0], [pos[1]]],
            "end_pos": [move[0], move[[1]]]
            }
            if self.valid_move(move_dict, piece.color):
                legal_moves.append([pos[0], pos[1]])
        
        return legal_moves