import _thread
import sched
import time
from pprint import pformat

import requests

from Logger import Logger
from MessageQuery import MessageQuery


class Bot:

    def __init__(self):
        self.__update_id = None

        # Token loading
        file = open("bot_token.txt", "r")
        self.__token = file.read()
        file.close()
        Logger.g().debug("Token loading : ", self.__token)

        # Load bot information
        get_info = self.__request_API("getMe")
        if get_info["ok"] is True:
            self.id = get_info["result"]["id"]
            self.first_name = get_info["result"]["first_name"]
            self.username = get_info["result"]["username"]
        else:
            Logger.g().critical("Incorrect Token")
            raise Exception("Incorrect Token !")

        self.s = sched.scheduler(time.time, time.sleep)
        self.task_count = 0

        # Print bot information
        Logger.g().info("Bot '", self.first_name, "' @", self.username, " | ID: ", self.id, " loaded successfully !")

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
            Logger.g().debug("API ", method, " - Requesting : ", path)

        result = f.json()
        if not silent:
            Logger.g().debug("API ", method, " - Result : \n", pformat(result))

        # Handle API error
        if result["ok"] is False and not silent:
            Logger.g().error("API ERROR - ", result["description"])
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
        if result.get("result") is None:
            Logger.g().debug("Unknown message: ", pformat(result))
            return
        for msg in result.get("result", []):
            self.__update_id = msg["update_id"] + 1
            query = MessageQuery(msg, self)
            try:
                resp, chat_id = query.handle()
                if resp is not None:
                    self.__send_message(resp, chat_id)
            except Exception as e:
                Logger.g().error("Exception occurred !", e, "\n", pformat(msg))
                tmp = msg.get("message")
                if tmp is not None:
                    if tmp.get("chat") is not None:
                        self.__send_message("An error occurred", tmp["chat"]["id"])

    def schedule_message(self, msg, seconds, chat_id):
        self.task_count += 1
        Logger.g().info("Scheduling message sending in", seconds, "seconds. Task count:", self.task_count)
        _thread.start_new_thread(self.__thread_schedule, (msg, seconds, chat_id))

    def __thread_schedule(self, msg, seconds, chat_id):
        self.s.enter(seconds, 1, self.__send_message, kwargs={'msg': msg, 'chat_id': chat_id, 'is_task': True})
        self.s.run()

    def __send_message(self, msg, chat_id, is_task=False):
        if is_task:
            self.task_count -= 1
            Logger.g().info("Task executed ! Task count:", self.task_count)
        return self.__request_API("sendMessage", method="POST", data={'text': msg, "chat_id": chat_id}, silent=True)
