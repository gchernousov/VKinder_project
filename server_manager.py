from server import Server
from config import token

from pprint import pprint as pp

if __name__ == "__main__":

    server = Server(token, 214337223, "Server")

    # server.send_msg(716417153, "test message")

    server.start()

    # pp(server.get_user_name(716417153))
    # pp(server.get_user_city(520397625))
