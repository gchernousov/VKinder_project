from server import Server
from config import token, group_id

if __name__ == "__main__":

    server = Server(token, group_id, "VKinder server")

    server.start()