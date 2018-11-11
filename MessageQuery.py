import re
from pprint import pprint, pformat

from Logger import Logger


class MessageQuery:

    def __init__(self, msg, bot):
        self.bot = bot
        self.debug_msg = msg
        self.is_edit = False
        self.is_inline = False
        self.is_group = False
        self.new_users = None
        self.group_name = None

        if msg.get("message") is not None:
            msg = msg["message"]
            if msg.get("new_chat_member"):
                self.new_users = msg["new_chat_members"]
            elif msg.get("left_chat_member"):
                Logger.g().debug("Group member leaving is not supported")
        elif msg.get("edited_message") is not None:
            msg = msg["edited_message"]
            self.is_edit = True
        elif msg.get("inline_query"):
            msg = msg["inline_query"]
            self.text = msg["inline_query"]["query"]
            self.is_inline = True
        else:
            Logger.g().error("Message type not supported")
            pprint(msg)
            return

        if not self.is_inline:
            self.text = msg.get("text")
            self.sticker = msg.get("sticker")
            self.document = msg.get("document")
            self.animation = msg.get("animation")
            self.photo = msg.get("photo")
            self.reply = True if msg.get("reply_to_message") is not None else False
            self.chat_id = msg["chat"]["id"]
            self.is_group = True if msg.get("chat") is not None and msg.get("chat").get("type") == "group" else False
            if self.is_group:
                self.group_name = msg.get("chat").get("title")

        self.username = msg["from"]["first_name"]
        self.user_code = msg["from"]["username"]
        self.lang = msg["from"].get("language_code")

    def print_debug(self):
        Logger.g().debug("Printing message data raw:\n", pformat(self.debug_msg))

    def handle(self):
        if self.is_edit:
            return "Command editing is not yet supported :'(", self.chat_id
        if self.reply:
            if self.is_group:
                return None
            return "Response is not yet supported :'(", self.chat_id

        # Group custom
        if self.is_group:
            ret = self.__handle_group_specific()
            if ret is not None:
                return ret, self.chat_id

        check = self.__type_error()
        if check is not None:
            return check, self.chat_id

        # Message handling
        if not self.is_inline:
            return self.__handle_message(), self.chat_id

        # Inline message handling
        elif self.is_inline:
            response = self.__handle_query()
            # print('Response:', response)
            # TODO inline response
            return None
        return None

    def __type_error(self):
        if self.text is None:
            msg = ""
            if self.sticker is not None:
                msg += "Stickers are"
            elif self.animation is not None:
                msg += "GIF are"
            elif self.document is not None:
                msg += "Documents are"
            elif self.photo is not None:
                msg += "Pictures are"
            else:
                Logger.g().info("Unrecognized message type")
                self.print_debug()
                msg += "This message is"
            msg += " not yet supported :'("
            return msg
        else:
            return None

    def __handle_message(self):
        # Send Hello message
        if re.match(r'^[/]?start$', self.text, re.IGNORECASE) or re.match(r'^[/]?help$', self.text, re.IGNORECASE):
            if self.lang == 'fr-FR' or self.lang == "fr":
                return self.__print_help_fr()
            else:
                return self.__print_help_en()
        elif re.match(r'^[/]?ping$', self.text, re.IGNORECASE):
            return "Pong"
        elif self.__hello_match() is not None:
            return self.__hello_match()
        else:
            return self.__handle_query()

    def __handle_group_specific(self):
        if self.new_users is not None:
            users_name = ""
            for user in self.new_users:
                # Detect self team joining
                if user.get("id") == self.bot.id:
                    if self.lang == 'fr-FR' or self.lang == "fr":
                        return self.__print_help_fr()
                    else:
                        return self.__print_help_en()
                else:
                    users_name += user.get("username") + " "
            if users_name != "":
                if self.lang == 'fr-FR' or self.lang == "fr":
                    return self.__welcome_message_fr(users_name)
                else:
                    return self.__welcome_message_en(users_name)

        return None

    def __handle_query(self):
        rule = r'^[/\\]?[ ]?(\d+)\s?(\w+)\s(.+)'
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
            Logger.g().error(resp)
            return resp
        # Seconds are default

        if self.chat_id is not None:
            self.bot.schedule_message(msg, delay_time, self.chat_id)
        else:
            Logger.g().debug("Send ", msg, " delayed ", time_nb, delay_time)
            return "Debug query"

        return "Query saved !"

    def __hello_match(self):
        if re.match(r'^[/]?(h[ea]llo|hi|good|hey)( ?.*)?$', self.text, re.IGNORECASE):
            resp = "Hello"
        elif re.match(r'^[/]?(salut|c(ou)?c(ou)?|bonjour|yop?)( ?.*)?$', self.text, re.IGNORECASE):
            resp = "Bonjour"
        elif re.match(r'^[/]?(th(ank)?[sx])( ?.*)?$', self.text, re.IGNORECASE):
            resp = "You're welcome"
        elif re.match(r'^[/]?(merci)( ?.*)?$', self.text, re.IGNORECASE):
            resp = "De rien"
        elif re.match(r'^[/]?(love|kiss|xoxo|<3|❤)( ?.*)?$', self.text, re.IGNORECASE):
            return "Thanks {0}, i have been code with love <3".format(self.username)
        elif re.match(r'^[/]?(sale con)( ?.*)?$', self.text, re.IGNORECASE):
            if re.match(r'^[/]?(Dramelac|LypsoSaleCon|MrTeishu)( ?.*)?$', self.user_code, re.IGNORECASE):
                return "A votre service sale con ;)"
            else:
                return None
        elif re.match(r'^[/]?(make me a |fais moi un )?(coffee?|caf[eé])( ?.*)?$', self.text, re.IGNORECASE):
            return """
Here it is !
   ( (
    ) )
.______.
|          |]
\          /
 `-----'"""
        elif re.match(r'^[/]?(make h(im|er) a |fais lui un )?(coffee?|caf[eé])( ?.*)?$', self.text, re.IGNORECASE):
            return "Does he drink coffee ?"
        elif re.match(r'^[/]?(SOS)( ?.*)?$', self.text, re.IGNORECASE):
            return "Looks like someone needs help ! Have you considered asking google ?\n" \
                   "WikiTITI is coming please wait..."
        else:
            return None
        return "{0} {1} :){2}".format(resp, self.username, " !" if re.match(r'.*!$', self.text) else "")

    def __print_help_fr(self):
        if self.is_group:
            target = "à tous"
            prefix = "/"
        else:
            target = self.username
            prefix = ""
        return "Bonjour {0} !\n" \
               "Je suis @MrDelayBot !\n" \
               "Je peux vous envoyer des messages dans le futur !\n" \
               "Syntax : \n" \
               "   \"{1}10s ce message me sera envoyé dans 10 secondes\"\n" \
               "   \"{1}1j ce message me sera envoyé dans 1 jour\"".format(target, prefix)

    def __print_help_en(self):
        if self.is_group:
            target = "everyone"
            prefix = "/"
        else:
            target = self.username
            prefix = ""
        return "Hello {0} !\n" \
               "I'm @MrDelayBot !\n" \
               "I can send you message in the futur !\n" \
               "Syntax : \n" \
               "   \"{1}10s this message will be sent to you in 10 seconds\"\n" \
               "   \"{1}1d this message will be sent to you in 1 day\"".format(target, prefix)

    def __welcome_message_fr(self, users):
        return "Bonjour {0}bienvenue sur {1} !".format(users, self.group_name)

    def __welcome_message_en(self, users):
        return "Hello {0}welcome on {1} !".format(users, self.group_name)

    @staticmethod
    def __get_syntax_error():
        return "Syntax Error. Please follow the correct \n" \
               "Example :\n" \
               "  \"5mn your message\"\n" \
               "  \"24h your message\""
