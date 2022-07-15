from server import Server
import configparser

settings = configparser.ConfigParser()
settings.read("settings.ini")

group_token = settings['VK_TOKENS']['group_token']
group_id = settings['VK_TOKENS']['group_id']


if __name__ == "__main__":

    server = Server(group_token, group_id, "VKinder server")

    server.start()