import re
from pprint import pformat

from Logger import Logger


class MessageQuery:

    def __init__(self, msg, bot, is_reply=False):
        self.bot = bot
        self.debug_msg = msg
        self.is_edit = False
        self.is_inline = False
        self.is_group = False
        self.is_reply = is_reply
        self.group_operation = False
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
        elif self.is_reply:
            self.text = msg.get('text')
        else:
            Logger.g().error("Message type not supported\n", pformat(msg))
            return

        if not self.is_inline:
            self.text = msg.get("text")
            self.sticker = msg.get("sticker")
            self.document = msg.get("document")
            self.animation = msg.get("animation")
            self.photo = msg.get("photo")
            self.group_operation = msg.get('left_chat_member') is not None
            self.reply = msg.get("reply_to_message") is not None
            if self.reply:
                self.reply_message = MessageQuery(msg.get("reply_to_message"), bot, is_reply=True)
            self.chat_id = msg["chat"]["id"]
            self.is_group = msg.get("chat") is not None and msg.get("chat").get("type") == "group"
            if self.is_group:
                self.group_name = msg.get("chat").get("title")

        self.username = msg["from"]["first_name"]
        self.user_code = msg["from"].get("username", "")
        self.lang = msg["from"].get("language_code", 'en')

    def print_debug(self):
        Logger.g().debug("Printing message data raw:\n", pformat(self.debug_msg))

    def handle(self):
        response_message = None
        if self.is_edit:
            response_message = "Message editing is not supported :'("
        # Group custom
        elif self.is_group:
            response_message = self.__handle_group_specific()
        else:
            check = self.__type_error()
            if check is not None:
                response_message = check

            # Message handling
            elif not self.is_inline:
                response_message = self.__handle_message()

            # Inline message handling
            elif self.is_inline:
                response = self.__handle_query()
                # print('Response:', response)
                # TODO inline response
                return "Inline message are not yet supported :'("
        return response_message, self.chat_id

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
            elif self.group_operation:
                return None
            else:
                Logger.g().info("Unrecognized message type")
                self.print_debug()
                msg += "This message is"
            msg += " not yet supported :'("
            return msg
        return None

    def __handle_message(self):
        if self.reply and not self.reply_message.__is_reply_message_valid():
            return None
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
        elif self.reply:
            return self.__handle_reply()
        else:
            return self.__handle_query()

    def __is_reply_message_valid(self):
        # Check if source message is from DelayBot
        if self.is_reply:
            from_data = self.debug_msg.get('from', {})
            if not from_data.get('is_bot') and from_data.get('username', '') != self.bot.username:
                return False
            # Exclude help and error messages
            if self.text in [self.__get_syntax_error(),
                             self.__print_help_en(),
                             self.__print_help_fr(),
                             "Query saved !",
                             "Up saved !",
                             "Up message in 24h !"]:
                return False
            return True
        return False

    def __handle_reply(self):
        if self.reply_message is not None and self.reply_message.__is_reply_message_valid():
            msg, delay_time = self.__time_command_parser(self.text, up_mode=True)
            if delay_time is None:
                return msg

            if self.chat_id is not None:
                self.bot.schedule_message(self.reply_message.text, delay_time, self.chat_id)
            else:
                Logger.g().debug("Send ", self.reply_message.text, " delayed ", delay_time)
                return "Debug up query"

            return "Up saved !" if msg is None else msg

        return None

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

    @staticmethod
    def compute_time(time_nb, time_type):
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
        # Week detection
        elif time_type == "w" or time_type == "week":
            delay_time = time_nb * 86400 * 7
        elif time_type != "s" and time_type != "sec":
            raise TypeError
        # Seconds are default
        return delay_time

    def __handle_query(self):

        msg, delay_time = self.__time_command_parser(self.text)
        if delay_time is None:
            return msg

        if self.chat_id is not None:
            self.bot.schedule_message(msg, delay_time, self.chat_id)
        else:
            Logger.g().debug("Send ", msg, " delayed ", delay_time)
            return "Debug query"

        return "Query saved !"

    @classmethod
    def __time_command_parser(cls, text, up_mode=False):
        result_time = None
        if up_mode:
            re_command = re.match(r'^[/\\]?(up\s)?(((\d+)([a-zA-Z]+))+)', text, re.DOTALL)
            # Match default /up
            if re.match(r'^[/\\]?up\s?$', text, re.DOTALL) is not None:
                return "Up message in 24h !", 60 * 60 * 24
            # Math custom up time '/up 1h' or '/1h'
            elif re_command is not None:
                return cls.__time_parser(re_command.group(2), None)
            else:
                return None, None  # Send nothing
        # Old limited time set
        # reout = re.match(r'^[/\\]?(\d+)([a-zA-Z]+)(\d+)?([a-zA-Z]+)?(\d+)?([a-zA-Z]+)?\s(.+)', text, re.DOTALL)
        # Match command time syntax
        re_global = re.match(r'^[/\\]?(([\d]+[a-zA-Z]+)+)\s(.+)', text, re.DOTALL)
        if re_global is None:
            result_text = cls.__get_syntax_error()
        else:
            time_command = re_global.group(1)
            message = re_global.group(3)
            result_text, result_time = cls.__time_parser(time_command, message)
        return result_text, result_time

    @classmethod
    def __time_parser(cls, time_text, msg):
        delay_time = 0
        time_type = "unknown"
        try:
            # Find all time from first part of text command
            matches = re.finditer(r"(\d+)([a-zA-Z]+)", time_text)
            for match in matches:
                time_nb = int(match.group(1))
                time_type = match.group(2)
                delay_time += MessageQuery.compute_time(time_nb, time_type)
        except TypeError:
            resp = "Time type '" + time_type + "' not understood :/"
            Logger.g().error(resp)
            msg = resp
            delay_time = None  # Delay time must be set to none to send error message immediately
        return msg, delay_time

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
        elif re.match(r'^[/]?(Dramelac|LypsoSaleCon|MrTeishu|Akumarachi)( ?.*)?$', self.user_code, re.IGNORECASE):
            if re.match(r'^[/]?(SOS)( ?.*)?$', self.text, re.IGNORECASE):
                name = "TITI"
                if re.match(r".*luci.*", self.text, re.IGNORECASE):
                    name = "LUCI"
                return "Looks like someone needs help ! Have you considered asking google ?\n" \
                       "Wiki{0} is coming please wait...".format(name)
            elif re.match(r'^[/]?(sale con)( ?.*)?$', self.text, re.IGNORECASE):
                return "A votre service sale con ;)"
            else:
                return None
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
               "Je suis @{1} !\n" \
               "Je peux vous envoyer des messages dans le futur !\n" \
               "Syntax : \n" \
               "   \"{2}10s ce message me sera envoyé dans 10 secondes\"\n" \
               "   \"{2}1j2h ce message me sera envoyé dans 1 jour et 2 heures\"".format(target,
                                                                                         self.bot.username,
                                                                                         prefix)

    def __print_help_en(self):
        if self.is_group:
            target = "everyone"
            prefix = "/"
        else:
            target = self.username
            prefix = ""
        return "Hello {0} !\n" \
               "I'm @{1} !\n" \
               "I can send you message in the futur !\n" \
               "Syntax : \n" \
               "   \"{2}10s this message will be sent to you in 10 seconds\"\n" \
               "   \"{2}1d2h this message will be sent to you in 1 day ans 2 hours\"".format(target,
                                                                                             self.bot.username,
                                                                                             prefix)

    def __welcome_message_fr(self, users):
        return "Bonjour {0}bienvenue sur {1} !".format(users, self.group_name)

    def __welcome_message_en(self, users):
        return "Hello {0}welcome on {1} !".format(users, self.group_name)

    @staticmethod
    def __get_syntax_error():
        return "Syntax Error. Please follow the correct \n" \
               "Example :\n" \
               "  \"5mn your message\"\n" \
               "  \"1d2h your message\""
