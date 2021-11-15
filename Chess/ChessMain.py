"""
Main driver file. User input
"""

import pygame as p
import ChessEngine

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

    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a valid move is made (so this doesnt happen every second)

    load_images()  # only this one time before while loop
    running = True
    selected_sq = ()  # no sq is selected, keep track of last click of the user
    player_clicks = []  # keep tact of players clicks (two tuples [(6,4]), (4,4)])
    two_players = False  # determine if playing against computer or another player

    # main game loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if selected_sq == (row, col):  # the user clicked the same sq twice
                    selected_sq = ()  # deselect
                    player_clicks = []  # clear player clicks
                else:
                    selected_sq = (row, col)
                    player_clicks.append(selected_sq)  # append both for 1st and 2nd click
                if len(player_clicks) == 2:  # after second click
                    if two_players:  # two player game
                        if gs.white_to_move:    # white move
                            move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        elif not gs.white_to_move:   # black move
                            #   translating clicks for black
                            player_clicks[0] = (7-player_clicks[0][0], 7-player_clicks[0][1])
                            player_clicks[1] = (7-player_clicks[1][0], 7-player_clicks[1][1])
                            move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    else:   # vs computer game
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:

                            gs.make_move(valid_moves[i])
                            move_made = True
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
        if move_made:  # generating moves only when valid move was made
            valid_moves = gs.get_valid_moves()
            move_made = False
        draw_game_state(screen, gs, two_players)
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Responsible for all the graphics within current game state
'''


def draw_game_state(screen, gs, two_players):
    draw_board(screen)  # draw squares on the board ##TODO: add piece highlights
    draw_pieces(screen, gs, two_players)  # draw pieces on squares
    if two_players and not gs.white_to_move:
        screen.blit(p.transform.rotate(screen, 180), (0, 0))


'''
Draw squares
'''


def draw_board(screen):
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Drawing pieces based on bord variable
'''


def draw_pieces(screen, gs, two_players):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = gs.board[r][c]
            if piece != "--":
                if two_players and not gs.white_to_move:
                    screen.blit(p.transform.rotate(IMAGES[piece], 180), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
