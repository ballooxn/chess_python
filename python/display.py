from termcolor import colored
from .piece import Piece

# 'w' = white, 'b' = black.
PIECES = {
    'w': {
        'k': '♚',
        'q': '♛',
        'r': '♜',
        'b': '♝',
        'n': '♞',
        'p': '♟',
    },
    'b': {
        "k": '♔',
        'q': '♕',
        'r': '♖',
        'b': '♗',
        'n': '♘',
        'p': '♙',
    }
}

def piece_to_symbol(piece):
    return PIECES[piece.color][piece.type]

def display_board(board):
    for i, row in enumerate(board):
        print(f"{8 - i} [ ", end='')
        for j, piece in enumerate(row):
            if j == 7:
                if piece == '_':
                    print(piece, end='')
                else:
                    print(piece_to_symbol(piece), end='')
            else:    
                if piece == '_':
                    print(f"{piece} ", end='')
                else:
                    print(f"{piece_to_symbol(piece)} ", end='')
        print("]")
    print("    a b c d e f g h")

def display_choose_move(player):
    message = f"{player.capitalize()}, please choose your move.\n"
    message += "Type it in the format '(first letter of piece)(current row OPTIONAL)(row to move)(column to move)'"
    message += "\nExample: knight on f5 to d4 --> nd4 OR nfd4\n"
    return message