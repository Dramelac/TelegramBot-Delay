import re


class MessageQuery:

    def __init__(self, msg, bot):
        self.bot = bot

        if msg.get("message") is not None:
            msg = msg["message"]
            self.text = msg.get("text")
            self.chat_id = msg["chat"]["id"]
            self.is_inline = False
        else:
            msg = msg["inline_query"]
            self.text = msg["inline_query"]["query"]
            self.is_inline = True

        self.username = msg["from"]["first_name"]
        self.lang = msg["from"].get("language_code")

    def handle(self):
        # Message handling
        if not self.is_inline:
            return self.__handle_message()

        # Inline message handling
        else:
            response = self.__handle_query()
            print('Response:', response)
            # TODO inline response
            return None

    def __handle_message(self):
        # Send Hello message
        if self.text == "/start" or self.text == "/help":
            if self.lang == 'fr-FR' or self.lang == "fr":
                return self.__print_help_fr(), self.chat_id
            else:
                return self.__print_help_en(), self.chat_id
        elif self.__hello_match():

            return 'Hello ' + self.username, self.chat_id
        else:
            return self.__handle_query(), self.chat_id

    def __handle_query(self):
        rule = r"(\d+)\s?(\w+)\s(.+)"
        reout = re.match(rule, self.text)
        if reout is None:
            return self.__get_syntax_error()
        try:
            time_nb = int(reout.group(1))
            time_type = reout.group(2)
            msg = reout.group(3)
        except IndexError:
            return self.__get_syntax_error()

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

        if self.chat_id is not None:
            self.bot.schedule_message(msg, delay_time, self.chat_id)
        else:
            print("[DEBUG] Send", msg, "delayed", time_nb, delay_time)
            return "Debug query"

        return "Query saved !"

    def __hello_match(self):
        pass

    def __print_help_fr(self):
        return "Bonjour " + self.username + " !\n" \
                                                 "Je suis @MrDelayBot !\n" \
                                                 "Je peux vous envoyer des messages dans le futur !\n" \
                                                 "Syntax : \n" \
                                                 "   \"10s ce message me sera envoyé dans 10 secondes\"\n" \
                                                 "   \"1j ce message me sera envoyé dans 1 jour\""

    def __print_help_en(self):
        return "Hello " + self.username + " !\n" \
                                               "I'm @MrDelayBot !\n" \
                                               "I can send you message in the futur !\n" \
                                               "Syntax : \n" \
                                               "   \"10s this message will be sent to you in 10 seconds\"\n" \
                                               "   \"1d this message will be sent to you in 1 day\""

    @staticmethod
    def __get_syntax_error():
        return "Syntax Error. Please follow the correct \n" \
               "Exemple :\n" \
               "  \"5mn your message\"\n" \
               " \"24h your message\""
