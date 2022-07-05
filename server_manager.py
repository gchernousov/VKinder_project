from server import Server
from config import token

from pprint import pprint as pp

GROUP_ID = 214337223

if __name__ == "__main__":

    server = Server(token, GROUP_ID, "VKinder server")

    server.start()