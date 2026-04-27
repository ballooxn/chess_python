from flask import Flask, render_template, jsonify, request
from python.game import Game
from python.board import Board

app = Flask(__name__)
game = Game()

def serialize_board():
    board = [[square.to_dict() if square != "_" else "_" for square in row] for row in game.board.board]

    return {
        'board': board,
        'current_player': game.current_player,
        'winner': game.winner
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/board')
def get_board():
    return jsonify(serialize_board())

@app.route('/move', methods=["POST"])
def move_piece():
    data = request.get_json()
    if not data:
        return jsonify({"error: Invalid move data"}), 400

    other_player = "b" if game.current_player == "w" else "w"

    if game.board.valid_move(data, game.current_player): #first letter: eg 'b' or 'w'
        piece = game.board.board[data["start_pos"][0]][data["start_pos"][1]]
        piece.times_moved += 1
        game.board.move_piece(data, game.current_player[0])

        # Check if other player is in checkmate (or stalemate in future)
        if game.board.in_checkmate(other_player):
            game.winner = game.current_player
        elif game.board.in_stalemate(other_player):
            game.winner = "stalemate"
        else:
            game.current_player = "w" if game.current_player == "b" else "b"

    return jsonify(serialize_board())

@app.route('/get_moves', methods=["POST"])
def get_moves():
    data = request.get_json()
    if not data:
        return jsonify({"error: Invalid get_moves data": 400})

    legal_moves = game.board.get_legal_moves(data["piece"], data["position"])
    return jsonify({"legal_moves": legal_moves})
        

@app.route('/reset', methods=["POST"])
def reset():
    global game
    game = Game()
    return jsonify(serialize_board())

if __name__ == "__main__":
    app.run(debug=True)

