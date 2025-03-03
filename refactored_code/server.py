import socket
from _thread import *
from board import Board
import pickle
import time

DEFAULT_PORT = 5555
BUFFER_SIZE = 24576
MAX_CONNECTIONS = 6
BOARD_SIZE = 8
GAME_TIME = 900
SMALL_BUFFER = 128

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "localhost"
port = DEFAULT_PORT

server_ip = socket.gethostbyname(server)

try:
    server_socket.bind((server, port))

except socket.error as e:
    print(str(e))

server_socket.listen()
print("[START] Waiting for a connection")

connections = 0

games = {0:Board(BOARD_SIZE, BOARD_SIZE)}

spectator_ids = [] 
spectator_count = 0

def read_specs():
    global spectator_ids

    spectator_ids = []
    try:
        with open("specs.txt", "r") as f:
            for line in f:
                spectator_ids.append(line.strip())
    except:
        print("[ERROR] No specs.txt file found, creating one...")
        open("specs.txt", "w")


def threaded_client(conn, game, spec=False):
    global pos, games, current_id, connections, spectator_count

    if not spec:
        player_name = None
        board = games[game]

        if connections % 2 == 0:
            current_id = "w"
        else:
            current_id = "b"

        board.start_user = current_id

        # Pickle the object and send it to the server
        data_string = pickle.dumps(board)

        if current_id == "b":
            board.ready = True
            board.start_time = time.time()

        conn.send(data_string)
        connections += 1

        while True:
            if game not in games:
                break

            try:
                d = conn.recv(BUFFER_SIZE)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    if data.count("select") > 0:
                        all = data.split(" ")
                        col = int(all[1])
                        row = int(all[2])
                        color = all[3]
                        board.select(col, row, color)

                    if data == "winner b":
                        board.winner = "b"
                        print("[GAME] Player b won in game", game)
                    if data == "winner w":
                        board.winner = "w"
                        print("[GAME] Player w won in game", game)

                    if data == "update moves":
                        board.update_moves()

                    if data.count("name") == 1:
                        player_name = data.split(" ")[1]
                        if current_id == "b":
                            board.player2_name = player_name
                        elif current_id == "w":
                            board.player1_name = player_name

                    #print("Recieved board from", current_id, "in game", game)

                    if board.ready:
                        if board.current_turn == "w":
                            board.player1_time = GAME_TIME - (time.time() - board.start_time) - board.stored_time1
                        else:
                            board.player2_time = GAME_TIME - (time.time() - board.start_time) - board.stored_time2

                    sendData = pickle.dumps(board)
                    #print("Sending board to player", current_id, "in game", game)

                conn.sendall(sendData)

            except Exception as e:
                print(e)
        
        connections -= 1
        try:
            del games[game]
            print("[GAME] Game", game, "ended")
        except:
            pass
        print("[DISCONNECT] Player", player_name, "left game", game)
        conn.close()

    else:
        available_games = list(games.keys())
        game_ind = 0
        board = games[available_games[game_ind]]
        board.start_user = "s"
        data_string = pickle.dumps(board)
        conn.send(data_string)

        while True:
            available_games = list(games.keys())
            board = games[available_games[game_ind]]
            try:
                d = conn.recv(SMALL_BUFFER)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    try:
                        if data == "forward":
                            print("[SPECTATOR] Moved Games forward")
                            game_ind += 1
                            if game_ind >= len(available_games):
                                game_ind = 0
                        elif data == "back":
                            print("[SPECTATOR] Moved Games back")
                            game_ind -= 1
                            if game_ind < 0:
                                game_ind = len(available_games) -1

                        board = games[available_games[game_ind]]
                    except:
                        print("[ERROR] Invalid Game Recieved from Spectator")

                    sendData = pickle.dumps(board)
                    conn.sendall(sendData)

            except Exception as e:
                print(e)

        print("[DISCONNECT] Spectator left game", game)
        spectator_count -= 1
        conn.close()


while True:
    read_specs()
    if connections < MAX_CONNECTIONS:
        conn, addr = server_socket.accept()
        spec = False
        game_id = -1
        print("[CONNECT] New connection")

        for game in games.keys():
            if games[game].ready == False:
                game_id=game

        if game_id == -1:
            try:
                game_id = list(games.keys())[-1]+1
                games[game_id] = Board(BOARD_SIZE,BOARD_SIZE)
            except:
                game_id = 0
                games[game_id] = Board(BOARD_SIZE,BOARD_SIZE)

        '''if addr[0] in spectator_ids and spectator_count == 0:
            spec = True
            print("[SPECTATOR DATA] Games to view: ")
            print("[SPECTATOR DATA]", games.keys())
            game_id = 0
            spectator_count += 1'''

        print("[DATA] Number of Connections:", connections+1)
        print("[DATA] Number of Games:", len(games))

        start_new_thread(threaded_client, (conn,game_id,spec))
