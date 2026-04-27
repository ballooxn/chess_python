# from .referee import 
from .display import display_board, display_choose_move
from .engine import Engine
from .board import Board
from .piece import Piece

import re

LETTER_TO_NUMBER = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

class Game:
    def __init__(self):
        self.board = Board()
        self.winner = None
        self.current_player = "w"