const piece_to_unicode = {
    'w': {'k': '♔', 'q': '♕', 'r': '♖', 'b': '♗', 'n': '♘', 'p': '♙'},
    'b': { 'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'}
}

let board_data = null
let selected_square = null
let move_list = []
let game_over = false

function get_piece_letter(piece) {
    if (!piece || piece === "_") return ""
    return (piece.type).toUpperCase()
}

function to_algebraic(row, col) {
    const files = 'abcdefgh'
    const file = files[col]
    const rank = 8 - row
    return file + rank;
}

function render_board(data) {
    board_data = data
    game_over = !!data.winner

    const player_turn = document.getElementById('player-turn')
    player_turn.textContent = data.current_player === 'w' ? 'White' : 'Black'

    const board_div = document.getElementById('board')
    board_div.innerHTML = ''

    data.board.forEach((row, row_index) => {
        row.forEach((square, col_index) => {
            const square_div = document.createElement('div')
            square_div.id = `${row_index}-${col_index}`
            square_div.dataset.row = row_index
            square_div.dataset.col = col_index

            const is_light = (row_index + col_index) % 2 === 0
            square_div.className = `square ${is_light ? 'light-square' : 'dark-square'}`

            if (square !== "_") {
                square_div.classList.add(square.color)
                square_div.textContent = piece_to_unicode[square.color][square.type]
            }

            square_div.addEventListener('click', handle_square_click)
            board_div.appendChild(square_div)
        })
    })

    const winner_div = document.getElementById('winner-div')
    const winner_text = document.getElementById('winner-text')

    if (data.winner) {
        winner_div.style.display = 'flex'
        if (data.winner === "stalemate") {
            winner_text.textContent = "Stalemate! Nobody wins."
        } else {
            const color_name = data.winner === "w" ? "White" : "Black"
            winner_text.textContent = `${color_name} wins!`
        }
    } else {
        winner_div.style.display = 'none'
    }
}

function get_legal_moves(piece, position) {
    fetch('/get_moves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            "position": position,
            "piece": piece
        })
    })
    .then(response => response.json())
    .then(new_data => {
        if (new_data["legal_moves"]) {
            console.log(new_data["legal_moves"])
            new_data["legal_moves"].forEach(move => {
                render_legal_square(move)
            })
        } else {
            console.log("No legal moves found")
        }
    })
    .catch(err => {
        console.error('Attempt to get legal moves failed', err)
    })
}

function render_legal_square(position) {
    console.log("rendering legal square")
    row = position[0]
    col = position[1]

    square = document.getElementById(`${row}-${col}`)
    square.classList.add('legal-move')

    if (board_data.board[position[0]][position[1]] !== "_") {
        square.classList.add('capture')
    }
}

function clear_legal_moves() {
    document.querySelectorAll('.legal-move').forEach(square => {
        square.classList.remove('legal-move', 'capture')
    })
}

function render_rank_labels() {
    const ranks_container = document.querySelector('.board-labels.ranks')
    if (!ranks_container) return
    ranks_container.innerHTML = ''

    for (let i = 8; i >= 1; i--) {
        const span = document.createElement('span')
        span.textContent = i
        ranks_container.appendChild(span)
    }
}

function render_file_labels() {
    const files_container = document.querySelector('.board-labels.files')
    if (!files_container) return
    files_container.innerHTML = ''

    const files =  ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    files.forEach(file => {
        const span = document.createElement('span')
        span.textContent = file
        files_container.appendChild(span)
    })
}

function render_move_list() {
    const move_list_div = document.getElementById('move-list')
    move_list_div.innerHTML = ''

    for (let i = 0; i < move_list.length; i += 2) {
        const row = document.createElement('div')
        row.className = 'move-row'

        const move_number = document.createElement('div')
        move_number.className = 'move-number'
        move_number.textContent = `${Math.floor(i / 2) + 1}.`
        row.appendChild(move_number)

        const white_move = document.createElement('div')
        white_move.className = 'move-white'
        white_move.textContent = move_list[i] || ''
        row.appendChild(white_move)

        const black_move = document.createElement('div')
        black_move.className = 'move-black'
        black_move.textContent = move_list[i + 1] || '';
        row.appendChild(black_move)

        move_list_div.appendChild(row)
    }

    move_list_div.scrollTop = move_list_div.scrollHeight
}

function handle_square_click(e) {
    if (!board_data || game_over) return;

    const row = parseInt(e.currentTarget.dataset.row);
    const col = parseInt(e.currentTarget.dataset.col);
    const piece = board_data.board[row][col];

    if (selected_square === null) {
        if (piece !== "_" && piece.color === board_data.current_player) {
            // we're clicking the piece we want to move
            selected_square = {row, col}
            highlight_selected()
            get_legal_moves(piece, [row, col])
        }
        return
    }
    const start_row = selected_square.row
    const start_col = selected_square.col

    // selected same piece - deselect
    if (row === start_row && col === start_col) {
        selected_square = null
        clear_legal_moves()
        highlight_selected()
        return
    }
    // selected piece of same color - switch selection
    if (piece !== "_" && piece.color === board_data.current_player) {
        selected_square = {row, col}
        highlight_selected()
        clear_legal_moves()
        get_legal_moves(piece, [row, col])
        return
    }

    // we're clicking a square to move to
    const start_alg = to_algebraic(start_row, start_col)
    const end_alg = to_algebraic(row, col)

    const moving_piece = board_data.board[start_row][start_col]
    const piece_letter = get_piece_letter(moving_piece)

    const move_notation = piece_letter ? `${piece_letter}${start_alg}-${end_alg}` : `${start_alg}-${end_alg}`

    const old_current = board_data.current_player
    const old_winner = board_data.winner

    fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_pos: [start_row, start_col],
            end_pos: [row, col]
        })
    })
    .then(response => response.json())
    .then(new_data => {
        const success = (new_data.current_player != old_current) || (new_data.winner !== old_winner)

        render_board(new_data)

        // if move was allowed and went through
        if (success) {
            move_list.push(move_notation)
            render_move_list()
        }

        selected_square = null
        highlight_selected()
    })
    .catch(err => {
        console.error('Move failed', err)
        selected_square = null
        highlight_selected()
    })
}   

function highlight_selected() {
    document.querySelectorAll('.square').forEach(sq => {
        sq.classList.remove('selected')
    })

    if (selected_square) {
        const id = `${selected_square.row}-${selected_square.col}`
        const square_element = document.getElementById(id)
        if (square_element) square_element.classList.add('selected')
    }
}

function setup_play_again() {
    const button = document.getElementById('play-again')
    button.addEventListener('click', () => {
        fetch('/reset', {method: 'POST'})
        .then(response => response.json())
        .then(new_data => {
            move_list = []
            render_move_list()
            render_board(new_data)
            selected_square = null
        })
    })
}

document.addEventListener('DOMContentLoaded', () => {
    fetch('/board')
    .then(response => response.json())
    .then(data => {
        render_board(data)
        render_move_list()
    })

    render_file_labels()
    render_rank_labels()

    setup_play_again()
})

// show all legal moves on gui
// 