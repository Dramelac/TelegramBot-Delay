import _thread
import sched
import time
import traceback
from pprint import pformat

import requests

from Logger import logger
from MessageQuery import MessageQuery


class Bot:

    def __init__(self):
        self.__update_id = None

        # Token loading
        file = open("bot_token.txt", "r")
        self.__token = file.read()
        file.close()
        logger.debug("Token loading : ", self.__token)

        # Load bot information
        self.__req = requests.session()
        get_info = self.__request_API("getMe")
        if get_info["ok"] is True:
            self.id = get_info["result"]["id"]
            self.first_name = get_info["result"]["first_name"]
            self.username = get_info["result"]["username"]
        else:
            logger.critical("Incorrect Token")
            raise Exception("Incorrect Token !")

        self.s = sched.scheduler(time.time, time.sleep)
        self.task_count = 0

        # Print bot information
        logger.info("Bot '", self.first_name, "' @", self.username, " | ID: ", self.id, " loaded successfully !")

    def __request_API(self, path, method="GET", data=None, silent=False):
        # Build URL
        url = "https://api.telegram.org/bot" + self.__token + "/" + path

        # Handle HTTP method
        if method == "GET":
            f = self.__req.get(url)
        elif method == "POST" and data is None:
            raise Exception("Data is missing")
        elif method == "POST":
            f = self.__req.post(url, data)
        else:
            raise Exception("Method unsupported")

        # Debug log
        if not silent:
            logger.debug("API ", method, " - Requesting : ", path)

        result = f.json()
        if not silent:
            logger.debug("API ", method, " - Result : \n", pformat(result))

        # Handle API error
        if result["ok"] is False and not silent:
            logger.error("API ERROR - ", result["description"])
        return result

    def pool_message(self):
        # Forge URI
        uri = "getUpdates"
        if self.__update_id is not None:
            uri += "?offset=" + str(self.__update_id)

        # Call API + reset update id
        result = self.__request_API(uri, silent=True)
        self.__update_id = None

        # Error handling
        error_code = result.get("error_code")
        if error_code is not None:
            # Catch server side error and 'Too Many Requests'
            if error_code >= 500 or error_code == 429:
                pass
            # Duplicate bot instance ?
            elif error_code == 409:
                logger.error('Conflict detected, Check if other bot is running ?')
                # exit(0)
            else:
                logger.error('Unknown response error : {}'.format(result))
            return

        # Handle messages
        if result.get("result") is None:
            logger.debug("Unknown message: ", pformat(result))
            return
        for msg in result.get("result", []):
            self.__update_id = msg["update_id"] + 1
            try:
                query = MessageQuery(msg, self)
                resp, chat_id = query.handle()
                if resp is not None:
                    self.__send_message(resp, chat_id)
            except Exception as e:
                logger.error("Exception occurred while responding !\nRequest:\n", pformat(msg),
                             "\n\nException details:\n", traceback.format_exc())
                tmp = msg.get("message")
                if tmp is not None:
                    if tmp.get("chat") is not None:
                        self.__send_message("An error occurred", tmp["chat"]["id"])

    def schedule_message(self, msg, seconds, chat_id):
        self.task_count += 1
        logger.info("Scheduling message sending in ", seconds, " seconds. Task count: ", self.task_count)
        _thread.start_new_thread(self.__thread_schedule, (msg, seconds, chat_id))

    def __thread_schedule(self, msg, seconds, chat_id):
        self.s.enter(seconds, 1, self.__send_message, kwargs={'msg': msg, 'chat_id': chat_id, 'is_task': True})
        self.s.run()

    def __send_message(self, msg, chat_id, is_task=False):
        if is_task:
            self.task_count -= 1
            logger.info("Task executed ! Task count: ", self.task_count)
        return self.__request_API("sendMessage", method="POST", data={'text': msg, "chat_id": chat_id}, silent=True)
