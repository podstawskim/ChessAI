import random
import requests
from ChessEngine import Move

piece_value = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}


knight_score = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

bishop_score = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

queen_score = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

rook_score = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

white_pawn_score = [
    [9, 9, 9, 9, 9, 9, 9, 9],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

black_pawn_score = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [9, 9, 9, 9, 9, 9, 9, 9],
]

king_score = [
    [0, 0, 9, 0, 0, 0, 12, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 9, 0, 0, 0, 12, 0],
]


piece_position_scores =  {"N": knight_score, "B": bishop_score, "Q": queen_score,
                          "R": rook_score, "bP": black_pawn_score, "wP": white_pawn_score, "K": king_score}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
global next_move

'''
Find random move
'''
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


'''
Find the best move based on material only (MinMax depth 2)
'''
def find_best_move_old(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1     # determining if -1 or 1 in evaluation based on color
    opp_minmax_score = CHECKMATE
    best_move = None
    random.shuffle(valid_moves)  # adding some randomization to computer moves
    for player_move in valid_moves:
        gs.make_move(player_move)
        opp_move = gs.get_valid_moves()
        opp_max_score = -CHECKMATE
        for opp_move in opp_move:
            gs.make_move(opp_move)
            if gs.checkmate:
                score = -turn_multiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(gs.board)
            if score > opp_max_score:
                opp_max_score = score
            gs.undo_move()
        # minimisation
        if opp_max_score < opp_minmax_score:
            opp_minmax_score = opp_max_score
            best_move = player_move
        best_move = player_move
        gs.undo_move()
    return best_move

'''
Min max algorithm checking every single position (MinMax recursively)
'''
def find_move_minmax(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:  # i want to evaluate board
        return score_material(gs.board)
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            gs.undo_move()
            score = find_move_minmax(gs, next_moves, depth-1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move

        return max_score

    else:
        min_score = CHECKMATE

        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            gs.undo_move()
            score = find_move_minmax(gs, next_moves, depth-1, True)
            if score < min_score:
                if depth == DEPTH:
                    next_move = move

        return min_score

'''
Helper method to make first recursive move !!!FAULTY!!! DONT USE
'''
def find_best_move(gs, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    # finding opening move
    next_move = get_opening_move(gs)
    if not next_move:
        find_move_negamax_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    return_queue.put(next_move)


def find_move_negamax(gs, valid_moves, depth, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move, engine_move=True)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax(gs, next_moves, depth-1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score

'''
Nega max algorithm with alpha beta pruning
'''
def find_move_negamax_alpha_beta(gs, valid_moves, depth, alpha, beta,turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move, engine_move=True)    # true only here
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax_alpha_beta(gs, next_moves, depth-1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print(move, score)
        gs.undo_move()
        if max_score > alpha: # pruning happens here
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

'''
Positive score - white winning, negative - black
'''
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE   # black wins
        else:
            return CHECKMATE

    if gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board)):
            sq = gs.board[row][col]
            if sq != "--":
                #score it positionally
                piece_position_score = 0
                if sq[1] == "K": # no position table for king
                    # TODO: check pieces around a king - if many ally pieces castling should be a good move
                    piece_position_score = piece_position_scores["K"][row][col] * .3
                    # if many pieces:
                    #piece_position_score = piece_position_scores["K"][row][col] * .3
                    # if less pieces:
                    # piece_position_score = piece_position_scores["K"][row][col] * .2

                elif sq[1] == "P": # for pawns
                    piece_position_score = piece_position_scores[sq][row][col] * .1
                else: # for rest of the pieces
                    piece_position_score = piece_position_scores[sq[1]][row][col] * .1
                if sq[0] == "w":
                    score += piece_value[sq[1]] + piece_position_score
                elif sq[0] == "b":
                    score -= piece_value[sq[1]] + piece_position_score
    return score


'''
Score the board based on material - old
'''
def score_material(board):
    score = 0
    for row in board:
        for sq in row:
            if sq[0] == "w":
                score += piece_value[sq[1]]
            elif sq[0] == "b":
                score -= piece_value[sq[1]]
    return score


'''
Responsible for retrieving opening move from masters database
'''

def get_opening_move(gs):
    uci_moves = get_moves_from_move_log(gs)
    url = "https://explorer.lichess.ovh/masters?play=" + uci_moves
    request = requests.get(url)
    if request:
        data = request.json()
    else:
        return None
    uci_move_text = None
    castle_move = False
    long_castle_move = False
    if len(data["moves"]) >= 1:
        move_number = random.randint(0, len(data["moves"])-1)
        uci_move_text = data["moves"][move_number]["uci"]
        san_move_text = data["moves"][move_number]["san"]
        if san_move_text == "O-O":  # castle
            castle_move = True
        if san_move_text == "O-O-O":    # long castle
            long_castle_move = True
        print("Database move " + uci_move_text)
    if uci_move_text:
        start_col, start_row, end_col, end_row = translate_chess_notation(uci_move_text)
        # TODO: check if move in valid moves
        if castle_move or long_castle_move:
            return Move((start_row, start_col), (end_row, end_col-1), gs.board, is_castle_move=True)
        return Move((start_row, start_col), (end_row, end_col), gs.board)
    return None


'''
Translating uci chess notation to rows and columns on gs.board
'''
def translate_chess_notation(move_text):
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    files_to_col = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    start_col = files_to_col[move_text[0]]
    start_row = ranks_to_rows[move_text[1]]
    end_col = files_to_col[move_text[2]]
    end_row = ranks_to_rows[move_text[3]]
    return start_col, start_row, end_col, end_row


'''
Creating move list from move log to send into get_opening_move
'''
def get_moves_from_move_log(gs):
    uci_moves = ''
    for m in gs.move_log:
        uci_moves += m.get_chess_notation() + ","
    uci_moves = uci_moves[:-1]  # removing last comma
    return uci_moves
