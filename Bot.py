from pprint import pprint

import requests


class Bot:

    def __init__(self):
        self.__update_id = None

        # Token loading
        file = open("bot_token.txt", "r")
        self.__token = file.read()
        file.close()
        print("Token loading :", self.__token)

        # Load bot information
        get_info = self.__request_API("getMe")
        if get_info["ok"] is True:
            self.id = get_info["result"]["id"]
            self.first_name = get_info["result"]["first_name"]
            self.username = get_info["result"]["username"]
        else:
            raise Exception("Incorrect Token !")

        # Print bot information
        print("Bot ", self.first_name, " / @", self.username, " | ID: ", self.id, " loaded successfully !", sep='')

    def __request_API(self, path, method="GET", data=None, silent=False):
        # Build URL
        url = "https://api.telegram.org/bot" + self.__token + "/" + path

        # Handle HTTP method
        if method == "GET":
            f = requests.get(url)
        elif method == "POST" and data is None:
            raise Exception("Data is missing")
        elif method == "POST":
            f = requests.post(url, data)
        else:
            raise Exception("Method unsupported")

        # Debug log
        if not silent:
            print("[API ", method, "] Requesting : ", path, sep='')
            print("[API ", method, "] Result : ", sep='')

        result = f.json()
        if not silent:
            pprint(result)

        # Handle API error
        if result["ok"] is False and not silent:
            print("[API ERROR]", result["description"])
        return result

    def pool_message(self):
        # Forge URI
        uri = "getUpdates"
        if self.__update_id is not None:
            uri += "?offset=" + str(self.__update_id)

        # Call API + reset update id
        result = self.__request_API(uri, silent=True)
        self.__update_id = None

        # Handle messages
        for msg in result["result"]:
            self.handle_message(msg)

    def handle_message(self, message):
        self.__update_id = message["update_id"] + 1

        # Message handling
        if message.get("message") is not None:
            msg = message["message"]
            txt = msg["text"]
            chat_id = msg["chat"]["id"]
            from_name = msg["from"]["first_name"]
            print('Received', txt, "from", from_name, "on chat id", chat_id)

            # Send Hello message
            if txt == "/start" or txt == "/help":
                self.print_help(chat_id)
            else:
                self.send_message("Hello " + from_name, chat_id)
        # Inline message handling
        elif message.get("inline_query") is not None:
            pass

    def send_message(self, msg, chat_id):
        result = self.__request_API("sendMessage", method="POST", data={'text': msg, "chat_id": chat_id})

    def print_help(self, chat_id):
        help_msg = "Bonjour !\n" \
                   "Je suis @MrDelayBot !\n" \
                   "Actuellement en développement, ce message n'est pas encore complet !"
        self.send_message(help_msg, chat_id)
