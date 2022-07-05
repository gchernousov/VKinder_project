from server import Server
from config import token

from pprint import pprint as pp

GROUP_ID = 214337223

if __name__ == "__main__":

    server = Server(token, GROUP_ID, "VKinder server")

    # server.send_msg(716417153, "test message")

    server.start()

    # pp(server.get_user_name(716417153))
    # pp(server.get_user_city(520397625))
