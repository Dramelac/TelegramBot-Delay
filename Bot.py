import _thread
import re
import sched
import time
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

        self.s = sched.scheduler(time.time, time.sleep)
        self.task_count = 0

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

            # Send Hello message
            if txt == "/start" or txt == "/help":
                if msg["from"]["language_code"] == 'fr-FR':
                    self.print_help_fr(chat_id, from_name)
                else:
                    self.print_help_en(chat_id, from_name)
            else:
                self.send_message(self.handle_query(txt, chat_id), chat_id)
        # Inline message handling
        elif message.get("inline_query") is not None:
            response = self.handle_query(message["inline_query"]["query"])
            print('Response:', response)

    def handle_query(self, query, chat_id=None):
        rule = r"(\d+)\s?(\w+)\s(.+)"
        reout = re.match(rule, query)
        if reout is None:
            return self.get_syntax_error()
        try:
            time_nb = int(reout.group(1))
            time_type = reout.group(2)
            msg = reout.group(3)
        except IndexError:
            return self.get_syntax_error()

        delay_time = time_nb
        # Minutes detection
        if time_type == "mn" or time_type == "m":
            delay_time = time_nb * 60
        # Hours detection
        elif time_type == "hr" or time_type == "h":
            delay_time = time_nb * 3600
        # Days detection
        elif time_type == "j" or time_type == "d":
            delay_time = time_nb * 86400
        elif time_type != "s" and time_type != "sec":
            resp = "Time type '" + time_type + "' not understood :/"
            print("[ERROR]", resp)
            return resp
        # Seconds are default

        if chat_id is not None:
            self.schedule_message(msg, delay_time, chat_id)
        else:
            print("[DEBUG] Send", msg, "delayed", time_nb, delay_time)
            return "Debug query"

        return "Query saved !"

    def schedule_message(self, msg, seconds, chat_id):
        self.task_count += 1
        print("[INFO] Scheduling message sending in", seconds, "seconds. Task count:", self.task_count)
        _thread.start_new_thread(self.__thread_schedule, (msg, seconds, chat_id))

    def __thread_schedule(self, msg, seconds, chat_id):
        self.s.enter(seconds, 1, self.send_message, kwargs={'msg': msg, 'chat_id': chat_id, 'is_task': True})
        self.s.run()

    @staticmethod
    def get_syntax_error():
        return "Syntax Error. Argument error.\n" \
               "Exemple :\n" \
               "  \"5mn your message\"\n" \
               " \"24h your message\""

    def send_message(self, msg, chat_id, is_task=False):
        if is_task:
            self.task_count -= 1
            print("[INFO] Task executed ! Task count:", self.task_count)
        return self.__request_API("sendMessage", method="POST", data={'text': msg, "chat_id": chat_id}, silent=True)

    def print_help_fr(self, chat_id, name):
        help_msg = "Bonjour " + name + " !\n" \
                                       "Je suis @MrDelayBot !\n" \
                                       "Je peux vous envoyer des messages dans le futur !\n" \
                                       "Syntax : \n" \
                                       "   \"10s ce message me sera envoyé dans 10 secondes\"\n" \
                                       "   \"1j ce message me sera envoyé dans 1 jour\""
        self.send_message(help_msg, chat_id)

    def print_help_en(self, chat_id, name):
        help_msg = "Hello " + name + " !\n" \
                                     "I'm @MrDelayBot !\n" \
                                     "I can send you message in the futur !\n" \
                                     "Syntax : \n" \
                                     "   \"10s this message will be sent to you in 10 seconds\"\n" \
                                     "   \"1d this message will be sent to you in 1 day\""
        self.send_message(help_msg, chat_id)
