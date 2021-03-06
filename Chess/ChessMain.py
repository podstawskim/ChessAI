"""
Main driver file. User input
"""

import pygame as p
import pygame.draw

import ChessEngine
import SmartMoveFinder
from multiprocessing import Process, Queue

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 is another option
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # chess board is 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


'''
Load images, initialize global dictionary of images. This will be called exactly once
'''
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'),
                                          (SQ_SIZE, SQ_SIZE))  # loading images and scaling them to square size


'''
Main driver for our code. User input and updating graphics
'''


def main():

    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))

    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 12, False, False)

    gs = ChessEngine.GameState()

    #default setting is for two players
    play_white = True # if human is playing white, then this will be true, if ai then this will be false
    play_black = True  # same as above but for black
    two_players = True if play_black and play_white else False
    one_player = True if (play_black and not play_white) or (play_white and not play_black) else False

    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a valid move is made (so this doesnt happen every second)
    animate = False
    load_images()  # only this one time before while loop
    running = True  # flag var for animation
    selected_sq = ()  # no sq is selected, keep track of last click of the user
    player_clicks = []  # keep tact of players clicks (two tuples [(6,4]), (4,4)])
    game_over = False
    ai_thinking = False
    move_finder_process = None
    move_undone = False

    # main game loop
    while running:

        human_turn = (gs.white_to_move and play_white) or (not gs.white_to_move and play_black)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if col >= 8:  # the user clicked the same sq twice or user clicked mouse log
                        selected_sq = ()  # deselect
                        player_clicks = []  # clear player clicks
                    else:
                        if (two_players and not gs.white_to_move) or (one_player and play_black):
                            selected_sq = (7-row, 7-col)
                        else:
                            selected_sq = (row, col)
                        player_clicks.append(selected_sq)  # append both for 1st and 2nd click
                    if len(player_clicks) == 2 and human_turn:  # after second click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_sq = ()  # resetting user clicks to 0
                                player_clicks = []
                        if not move_made:
                            player_clicks = [selected_sq]  # fixing error clicks (deselecting pieces)
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undo_move()
                    selected_sq = ()
                    player_clicks = []
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                # if e.key == p.K_r:  # reset board when 'r' is pressed
                #     gs = ChessEngine.GameState()
                #     valid_moves = gs.get_valid_moves()
                #     selected_sq = ()
                #     player_clicks = []
                #     move_made = False
                #     animate = False
                #     game_over = False
                #     if ai_thinking:
                #         move_finder_process.terminate()
                #         ai_thinking = False
                #     move_undone = True
                if e.key == p.K_t: # switch to two player game
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    two_players = True
                    one_player = False
                    play_black = True
                    play_white = True
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                if e.key == p.K_b: # switch to one player game as black
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    two_players = False
                    one_player = True
                    play_white = False
                    play_black = True
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                if e.key == p.K_w: # switch to one player game as black
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    two_players = False
                    one_player = True
                    play_white = True
                    play_black = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False



        #AI move finder logic
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                print("thinking...")
                return_queue = Queue() # used to pass data between threads
                move_finder_process = Process(target=SmartMoveFinder.find_best_move, args=(gs, valid_moves, return_queue))
                move_finder_process.start() #call find_best_move()

            if not move_finder_process.is_alive():
                print("done thinking")
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = SmartMoveFinder.find_random_move(valid_moves)
                gs.make_move(ai_move)
                move_made = True
                animate = True
                ai_thinking = False
                # fixing bug - after ai done thinking sometimes user had to click twice on own piece to move it
                player_clicks = []
                selected_sq = ()

        if move_made:  # generating moves only when valid move was made
            #if animate:
                #animate_move(gs.move_log[-1], screen, clock, gs, one_player, two_players, play_black)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

        draw_game_state(screen, gs, valid_moves, selected_sq, move_log_font, one_player, two_players, play_white, play_black)

        if gs.checkmate or gs.stalemate:
            game_over = True
            text = "Stalemate" if gs.stalemate else "Black wins by checkmate" if gs.white_to_move else "White wins by checkmate"
            draw_endgame_text(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all the graphics within current game state
'''
def draw_game_state(screen, gs, valid_moves, selected_sq, move_log_font, one_player, two_players, play_white, play_black):
    draw_board(screen, gs)  # draw squares on the board
    highlight_squares(screen, gs, valid_moves, selected_sq)
    draw_pieces(screen, gs, one_player, two_players, play_black)  # draw pieces on squares
    if two_players and not gs.white_to_move:
        screen.blit(p.transform.rotate(screen, 180), (-MOVE_LOG_PANEL_WIDTH, 0)) # -MOVE_LOG_PANEL_WIDTH to properly display log panel
    if one_player and play_black:
        screen.blit(p.transform.rotate(screen, 180),
                    (-MOVE_LOG_PANEL_WIDTH, 0))  # -MOVE_LOG_PANEL_WIDTH to properly display log panel

    draw_move_log(screen, gs, move_log_font)


'''
Draw squares
'''
def draw_board(screen, gs):
    global colors
    colors = [p.Color(238,238,210), p.Color(118,150,86)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    highlight_last_move(screen, gs)

'''
Highlighting selected piece and moves for that piece
'''
def highlight_squares(screen, gs, valid_moves, selected_sq):

    if selected_sq != ():
        r, c = selected_sq
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):     # making sure that sq seleceted is piece that can move
            # highlighting sq
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)    # transparency value
            s.fill(p.Color(186,202,68))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from tha sq
            s.fill(p.Color(61, 72, 73))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

'''
Drawing pieces based on bord variable
'''
def draw_pieces(screen, gs, one_player, two_players, play_black, animation=False):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = gs.board[r][c]
            if piece != "--":
                if (two_players and not gs.white_to_move and not animation) or (one_player and play_black and not animation):
                    screen.blit(p.transform.rotate(IMAGES[piece], 180), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                elif two_players and not gs.white_to_move and animation:
                    screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                elif one_player and play_black and animation:
                    screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))



'''
Draws a move log
'''
def draw_move_log(screen, gs, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i//2 + 1) + ". " + str(move_log[i]) + " "
        if i + 1 < len(move_log): # make sure black made a move
            move_string += str(move_log[i+1]) + " "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = font.render(text, True, p.Color("White"))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height()


'''
Animating a move
'''
def animate_move(move, screen, clock, gs, one_player, two_players, play_black):
    global colors
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frames_per_sq = 5
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_sq
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_r * frame/frame_count, move.start_col + d_c * frame/frame_count)
        draw_board(screen, gs)
        draw_pieces(screen, gs, one_player, two_players, play_black, True)
        # erase moved piece from end sq
        color = colors[(move.end_row + move.end_col) % 2]
        end_sq = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_sq)
        # draw captured pieces on rectangle
        if move.piece_captured != "--":
            if move.enpassant:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_sq = p.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_sq)
        # draw moving piece
        if move.piece_moved != "--":
            screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


'''
Responsible for highlighting last move made
'''
def highlight_last_move(screen, gs):
    if len(gs.move_log) != 0:
        last_move = gs.move_log[len(gs.move_log)-1] # gets last move
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.fill(p.Color("yellow"))
        s.set_alpha(100)  # transparency value
        screen.blit(s, (last_move.start_col * SQ_SIZE, last_move.start_row * SQ_SIZE))
        screen.blit(s, (last_move.end_col * SQ_SIZE, last_move.end_row * SQ_SIZE))


def draw_endgame_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, True, p.Color("Black"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, True, p.Color("Grey"))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()
