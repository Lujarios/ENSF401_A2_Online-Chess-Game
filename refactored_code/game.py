'''
the main game
author:@techwithtim
requirements:see requirements.txt
'''

import subprocess
import sys
import get_pip

BOARD_DIM = (750, 750)
BOARD_X = 113
BOARD_Y = 113
BOARD_WIDTH = 525
FRAME_UPDATE_INTERVAL = 60
FONT_SIZE_EXTRA_SMALL = 30
FONT_SIZE_SMALL = 50
FONT_SIZE_LARGE = 80
PLAYER_1_TIME_POS = (520, 10)
PLAYER_2_TIME_POS = (520, 700)
SPECTATOR_MODE_Y = 10
WAITING_MESSAGE_Y = 300
TURN_INDICATOR_Y = 700
QUIT_MESSAGE_POS = (10, 20)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)


def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    print("[GAME] Trying to import pygame")
    import pygame
except:
    print("[EXCEPTION] Pygame not installed")

    try:
        print("[GAME] Trying to install pygame via pip")
        import pip
        install("pygame")
        print("[GAME] Pygame has been installed")
    except:
        print("[EXCEPTION] Pip not installed on system")
        print("[GAME] Trying to install pip")
        get_pip.main()
        print("[GAME] Pip has been installed")
        try:
            print("[GAME] Trying to install pygame")
            import pip
            install("pygame")
            print("[GAME] Pygame has been installed")
        except:
            print("[ERROR 1] Pygame could not be installed")


import pygame
import os
import time
from client import Network
import pickle
pygame.font.init()

board = pygame.transform.scale(pygame.image.load(os.path.join("img","board_alt.png")), BOARD_DIM)
chess_background = pygame.image.load(os.path.join("img", "chess_background.png"))
board_rect = (BOARD_X,BOARD_Y,BOARD_WIDTH,BOARD_WIDTH)

current_turn = "w"


def menu_screen(win, player_name):
    global board, chess_background
    run = True
    offline = False

    while run:
        win.blit(chess_background, (0,0))
        small_font = pygame.font.SysFont("comicsans", FONT_SIZE_SMALL)
        
        if offline:
            off = small_font.render("Server Offline, Try Again Later...", 1, COLOR_RED)
            win.blit(off, (width / 2 - off.get_width() / 2, 500))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                offline = False
                try:
                    board = connect()
                    run = False
                    main()
                    break
                except:
                    print("Server Offline")
                    offline = True


    
def redraw_gameWindow(win, board, p1, p2, color, ready):
    win.blit(board, (0, 0))
    board.draw(win, color)

    formatTime1 = str(int(p1//FRAME_UPDATE_INTERVAL)) + ":" + str(int(p1%FRAME_UPDATE_INTERVAL))
    formatTime2 = str(int(p2 // FRAME_UPDATE_INTERVAL)) + ":" + str(int(p2 % FRAME_UPDATE_INTERVAL))
    if int(p1%FRAME_UPDATE_INTERVAL) < SPECTATOR_MODE_Y:
        formatTime1 = formatTime1[:-1] + "0" + formatTime1[-1]
    if int(p2%FRAME_UPDATE_INTERVAL) < SPECTATOR_MODE_Y:
        formatTime2 = formatTime2[:-1] + "0" + formatTime2[-1]

    font = pygame.font.SysFont("comicsans", FONT_SIZE_EXTRA_SMALL)
    try:
        txt = font.render(board.player1_name + "\'s Time: " + str(formatTime2), 1, COLOR_WHITE)
        txt2 = font.render(board.player2_name + "\'s Time: " + str(formatTime1), 1, COLOR_WHITE)
    except Exception as e:
        print(e)
    win.blit(txt, PLAYER_1_TIME_POS)
    win.blit(txt2, PLAYER_2_TIME_POS)

    txt = font.render("Press q to Quit", 1, COLOR_WHITE)
    win.blit(txt, QUIT_MESSAGE_POS)

    if color == "s":
        txt3 = font.render("SPECTATOR MODE", 1, COLOR_RED)
        win.blit(txt3, (width/2-txt3.get_width()/2, SPECTATOR_MODE_Y))

    if not ready:
        show = "Waiting for Player"
        if color == "s":
            show = "Waiting for Players"
        font = pygame.font.SysFont("comicsans", FONT_SIZE_LARGE)
        txt = font.render(show, 1, COLOR_RED)
        win.blit(txt, (width/2 - txt.get_width()/2, WAITING_MESSAGE_Y))

    if not color == "s":
        font = pygame.font.SysFont("comicsans", FONT_SIZE_EXTRA_SMALL)
        if color == "w":
            txt3 = font.render("YOU ARE WHITE", 1, COLOR_RED)
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, SPECTATOR_MODE_Y))
        else:
            txt3 = font.render("YOU ARE BLACK", 1, COLOR_RED)
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, SPECTATOR_MODE_Y))

        if board.current_turn == color:
            txt3 = font.render("YOUR TURN", 1, COLOR_RED)
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, TURN_INDICATOR_Y))
        else:
            txt3 = font.render("THEIR TURN", 1, COLOR_RED)
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, TURN_INDICATOR_Y))

    pygame.display.update()


def end_screen(win, text):
    pygame.font.init()
    font = pygame.font.SysFont("comicsans", FONT_SIZE_LARGE)
    txt = font.render(text,1, COLOR_RED)
    win.blit(txt, (width / 2 - txt.get_width() / 2, WAITING_MESSAGE_Y))
    pygame.display.update()

    pygame.time.set_timer(pygame.USEREVENT+1, 3000)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                run = False
            elif event.type == pygame.KEYDOWN:
                run = False
            elif event.type == pygame.USEREVENT+1:
                run = False


def click(pos):
    """
    :return: pos (x, y) in range 0-7 0-7
    """
    x = pos[0]
    y = pos[1]
    if board_rect[0] < x < board_rect[0] + board_rect[2]:
        if board_rect[1] < y < board_rect[1] + board_rect[3]:
            divX = x - board_rect[0]
            divY = y - board_rect[1]
            i = int(divX / (board_rect[2]/8))
            j = int(divY / (board_rect[3]/8))
            return i, j

    return -1, -1


def connect():
    global n
    n = Network()
    return n.board


def main():
    global current_turn, board, player_name

    color = board.start_user
    count = 0

    board = n.send("update_moves")
    board = n.send("name " + player_name)
    clock = pygame.time.Clock()
    run = True

    while run:
        if not color == "s":
            player1_time = board.player1_time
            player2_time = board.player2_time
            if count == FRAME_UPDATE_INTERVAL:
                board = n.send("get")
                count = 0
            else:
                count += 1
            clock.tick(30)

        try:
            redraw_gameWindow(win, board, player1_time, player2_time, color, board.ready)
        except Exception as e:
            print(e)
            end_screen(win, "Other player left")
            run = False
            break

        if not color == "s":
            if player1_time <= 0:
                board = n.send("winner b")
            elif player2_time <= 0:
                board = n.send("winner w")

            if board.check_mate("b"):
                board = n.send("winner b")
            elif board.check_mate("w"):
                board = n.send("winner w")

        if board.winner == "w":
            end_screen(win, "White is the Winner!")
            run = False
        elif board.winner == "b":
            end_screen(win, "Black is the winner")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and color != "s":
                    # quit game
                    if color == "w":
                        board = n.send("winner b")
                    else:
                        board = n.send("winner w")

                if event.key == pygame.K_RIGHT:
                    board = n.send("forward")

                if event.key == pygame.K_LEFT:
                    board = n.send("back")


            if event.type == pygame.MOUSEBUTTONUP and color != "s":
                if color == board.current_turn and board.ready:
                    pos = pygame.mouse.get_pos()
                    board = n.send("update moves")
                    i, j = click(pos)
                    board = n.send("select " + str(i) + " " + str(j) + " " + color)
    
    n.disconnect()
    board = 0
    menu_screen(win)


player_name = input("Please type your player_name: ")
width = BOARD_DIM[0]
height = BOARD_DIM[1]
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess Game")
menu_screen(win, player_name)
