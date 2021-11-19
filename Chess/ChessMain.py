"""
Main driver file. User input
"""

import pygame as p
import ChessEngine
import time

p.init()
WIDTH = HEIGHT = 512  # 400 is another option
DIMENSION = 8  # chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
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
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    play_as_black = True
    gs = ChessEngine.GameState()
    gs.white_to_move = not gs.white_to_move
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a valid move is made (so this doesnt happen every second)
    animate = False
    load_images()  # only this one time before while loop
    running = True  # flag var for animation
    selected_sq = ()  # no sq is selected, keep track of last click of the user
    player_clicks = []  # keep tact of players clicks (two tuples [(6,4]), (4,4)])
    game_over = False


    # main game loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    print(col, row)
                    if selected_sq == (row, col):  # the user clicked the same sq twice
                        selected_sq = ()  # deselect
                        player_clicks = []  # clear player clicks
                    else:
                        selected_sq = (row, col)
                        player_clicks.append(selected_sq)  # append both for 1st and 2nd click
                    if len(player_clicks) == 2:  # after second click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_sq = ()  # resetting user clicks to 0
                                player_clicks = []
                                print(move.get_chess_notation())
                        if not move_made:
                            player_clicks = [selected_sq]  # fixing error clicks (deselecting pieces)
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    if game_over:
                        game_over = not game_over
                if e.key == p.K_r:  # reset board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        if move_made:  # generating moves only when valid move was made
            #if animate:
                #animate_move(gs.move_log[-1], screen, gs.board, clock, play_as_black)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, selected_sq, play_as_black)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, "White wins by checkmate")
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


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
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from tha sq
            s.fill(p.Color("green"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

'''
Responsible for all the graphics within current game state
'''
def draw_game_state(screen, gs, valid_moves, selected_sq, play_as_black):
    draw_board(screen)  # draw squares on the board
    highlight_squares(screen, gs, valid_moves, selected_sq)
    draw_pieces(screen, gs.board, play_as_black)  # draw pieces on squares



'''
Draw squares
'''
def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Drawing pieces based on bord variable
'''
def draw_pieces(screen, board, play_as_black):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                if play_as_black:
                    if piece[0] == "w":
                        piece = piece.replace('w', 'b')
                    elif piece[0] == "b":
                        piece = piece.replace('b', 'w')
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Animating a move
'''
def animate_move(move, screen, board, clock, play_as_black):
    global colors
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frames_per_sq = 5
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_sq
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_r * frame/frame_count, move.start_col + d_c * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board, play_as_black)
        # erase moved piece from end sq
        color = colors[(move.end_row + move.end_col) % 2]
        end_sq = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_sq)
        # draw captured pieces on rectangle
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_sq)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, True, p.Color("Black"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, True, p.Color("Grey"))
    screen.blit(text_object, text_location.move(2, 2))



if __name__ == "__main__":
    main()
