"""
Storing all the information about current state of a chess game. Determining valid moves. Move log.
"""


class GameState:
    def __init__(self, play_as_black=False):
        # the board is 8x8 2 D list, element is two characters: 1st- color, 2nd - piece
        # '--' represents empty square
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]


        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               "B": self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.play_as_black = play_as_black
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = ()  # coordinates for a sq where en passant capture is possible
        self.current_castling_rights = Castle(True, True, True, True)
        self.castle_rights_log = [Castle(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                         self.current_castling_rights.bks, self.current_castling_rights.bqs)]

    '''
    Takes a move as a parameter and executes it (no castling, pawn promotion, en passant)
    '''

    def make_move(self, move):
        if self.board[move.start_row][move.start_col] != '--':  # prevents from disappearing pieces
            self.board[move.start_row][
                move.start_col] = "--"  # we moved piece from this square so we have to make it empty
            self.board[move.end_row][move.end_col] = move.piece_moved
            # no validation right now
            self.move_log.append(move)  # logging move so we can undo it
            self.white_to_move = not self.white_to_move  # swapping players
            # update the king's location when moved
            if move.piece_moved == "wK":
                self.white_king_location = (move.end_row, move.end_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.end_row, move.end_col)

            # pawn promotion
            if move.pawn_promotion:
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"
            # en passant
            # if pawn moved twice the next move can be en passant
            if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ((move.end_row + move.start_row) // 2, move.end_col)
            else:
                self.enpassant_possible = ()
            # if en passant move must update board to capture the pawn
            if move.enpassant:
                self.board[move.start_row][move.end_col] = "--"

            # castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside castle
                    self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]    # moves the rook
                    self.board[move.end_row][move.end_col+1] = "--"
                else:   # queen side castle
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]     # moves the rook
                    self.board[move.end_row][move.end_col-2] = "--"
            # update castling rights - whenever rook or a king moves
            self.update_castle_rights(move)
            self.castle_rights_log.append(Castle(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                                 self.current_castling_rights.bks, self.current_castling_rights.bqs))



    '''
    Undo last move
    '''

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # switch turns back
            # update kings position
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            # undo en passant move
            if move.enpassant:
                self.board[move.end_row][move.end_col] = "--"  # landing sq
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            # undo 2 sq pawn advance
            if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()
            # undo castling rights
            self.castle_rights_log.pop()  # get rid of the new castle rights we are undoing
            self.current_castling_rights = self.castle_rights_log[-1]  # set the current castle rights to the last one in the list
            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col-1] = "--"
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"
            self.checkmate = False
            self.stalemate = False

    '''
    Update castle rights depending on which rook/king was moved
    '''

    def update_castle_rights(self, move):
        # if rook was captured
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_col == 0:   # left rook captured
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:     # right rook captured
                    self.current_castling_rights.wks = False
        if move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_col == 0:   # left rook captured
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:     # right rook captured
                    self.current_castling_rights.bks = False
        # if king or rook was moved
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False

    '''
    All moves considering checks
    '''

    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.get_all_possible_moves()
                # to block a check you have to move piece into one of the squares between enemy piece and the king
                check = self.checks[0]  # check info
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]  # enemy piece causing check
                valid_squares = []  # squares that piece can move to
                # if knight - capture it, or move king
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        # check[2] and check[3] are the check directions
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        # once you get to checking piece, end check
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # get rid of any move that is not blocking a check or is a  valid king move
                for i in range(len(moves) - 1, -1, -1):
                    # king wasn't moved, so capture or block must occur
                    if moves[i].piece_moved[1] != "K":
                        # move doesn't block a check or capture piece applying check
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:
            # not a check so any move is fine
            moves = self.get_all_possible_moves()

        # check if checkmate or stalemate occurred
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.stalemate = False
            self.checkmate = False

        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        return moves

    '''
    Returns if player is in check, list of pins and checks
    '''

    def check_for_pins_and_checks(self):
        pins = []  # squares where allied pieces are pinned, and direction pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check squares outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # 1st allied piece, could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # 2nd allied piece, so no pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # 5 possibilities
                        # 1. orthogonally away from the king and piece is a rook
                        # 2. diagonally from the king and a piece is a bishop
                        # 3. 1 sq away from king a piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 sq away from the king and enemy piece is a king
                        if (0 <= j <= 3 and piece_type == "R") or \
                                (4 <= j <= 7 and piece_type == "B") or \
                                (i == 1 and piece_type == "P" and ((enemy_color == "w" and 6 <= j <= 7) or (
                                        enemy_color == "b" and 4 <= j <= 5))) or \
                                (piece_type == "Q") or (i == 1 and piece_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece is blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece but not applying check
                            break
                else:  # off board break
                    break

        knight_moves = ((-2, -1), (-1, -2), (-2, 1), (2, -1), (-1, 2), (1, -2), (1, 2), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # check if it is a enemy knight attacking king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

    '''
    Determine if the enemy can attack sq r, c
    '''

    def sq_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move  # switch to opponents moves
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # switch turns back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:  # sq is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in given row
                turn = self.board[r][c][0]
                if self.play_as_black:
                    if turn == "w":
                        turn = "b"
                    elif turn == "b":
                        turn = "w"
                    if (turn == 'w' and not self.white_to_move) or (turn == 'b' and self.white_to_move):
                        piece = self.board[r][c][1]
                        self.move_functions[piece](r, c, moves)  # calls appropriate move functions
                elif (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)  # calls appropriate move functions

        return moves

    '''
    Get all pawn moves for the paw to located at row, col and add these moves to the list
    '''

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = "b"
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = "w"
        pawn_promotion = False
        if self.board[r + move_amount][c] == "--":  # 1 sq move
            if not piece_pinned or pin_direction == (move_amount, 0):
                if r + move_amount == back_row:  # if piece gets to back rank it is a pawn promotion
                    pawn_promotion = True
                moves.append(Move((r, c), (r + move_amount, c), self.board, pawn_promotion=pawn_promotion))
                if r == start_row and self.board[r + 2 * move_amount][c] == "--":  # 2 sq moves
                    moves.append(Move((r, c), (r + 2 * move_amount, c), self.board))
        if c - 1 >= 0:  # capture to left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    if r + move_amount == back_row:  # if piece get to back rank it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board, pawn_promotion=pawn_promotion))
                if (r + move_amount, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board, enpassant=True))
        if c + 1 <= 7:  # capture to left
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    if r + move_amount == back_row:  # if piece get to back rank it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board, pawn_promotion=pawn_promotion))
                if (r + move_amount, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board, enpassant=True))

    '''
    Get all rook moves for the pawn to located at row, col and add these moves to the list
    '''

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # end of board
                    if not piece_pinned or pin_direction == d or pin_direction == (
                            -d[0], -d[1]):  # bishop and rook can move back in direction of the pin
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece, invalid
                            break
                else:  # off board
                    break

    '''
    Get all rook knight for the pawn to located at row, col and add these moves to the list
    '''

    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        directions = ((-2, -1), (-1, -2), (-2, 1), (2, -1), (-1, 2), (1, -2), (1, 2), (2, 1))
        ally_color = "w" if self.white_to_move else "b"
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # end of board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    '''
    Get all bishop moves for the pawn to located at row, col and add these moves to the list
    '''

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty sq valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    '''
    Get all queen moves for the pawn to located at row, col and add these moves to the list
    '''

    def get_queen_moves(self, r, c, moves):
        # queen moves as bishop and rook combined
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    '''
    Get all king moves for the pawn to located at row, col and add these moves to the list
    '''

    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece (empty or enemy piece)
                    # place a king on square and check for check
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)


    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''

    def get_castle_moves(self, r, c, moves):

        if self.sq_under_attack(r, c):  # cant castle if in check
            return
        if (self.white_to_move and self.current_castling_rights.wks) or (
                not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_move(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (
                not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_move(r, c, moves)

    '''
    Check if squares kingside are empty and are not under attack
    '''
    def get_kingside_castle_move(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.sq_under_attack(r, c + 1) and not self.sq_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    '''
    Check if squares queenside are empty and are not under attack 
    '''
    def get_queenside_castle_move(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.sq_under_attack(r, c - 1) and not self.sq_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))


class Castle:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:
    # mapping keys to values
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_col = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    col_to_files = {v: k for k, v in files_to_col.items()}

    def __init__(self, start_sq, end_sq, board, enpassant=False, pawn_promotion=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # pawn promotion
        self.pawn_promotion = pawn_promotion
        # enpassant
        self.enpassant = enpassant
        if self.enpassant:
            self.piece_captured = "bP" if self.piece_moved == "wP" else "wP"
        # castle move
        self.is_castle_move = is_castle_move

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col  # hashing to be able to compare moves

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        # TODO: create real chess notation
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)




    def get_rank_file(self, r, c):
        return self.col_to_files[c] + self.rows_to_ranks[r]
