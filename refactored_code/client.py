import socket
import pickle
import time

DEFAULT_PORT = 5555
BUFFER_SIZE = 32768
TIMEOUT_LIMIT = 5

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        self.port = DEFAULT_PORT
        self.addr = (self.host, self.port)
        self.board = self.connect()
        self.board = pickle.loads(self.board)

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(BUFFER_SIZE)

    def disconnect(self):
        self.client.close()

    def send(self, data, use_pickle=False):
        """
        :param data: str
        :return: str
        """
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_LIMIT:
            try:
                if use_pickle:
                    self.client.send(pickle.dumps(data))
                else:
                    self.client.send(str.encode(data))
                response = self.client.recv(BUFFER_SIZE)
                try:
                    response = pickle.loads(response)
                    break
                except Exception as e:
                    print(e)

            except socket.error as e:
                print(e)


        return response


