import logging
import os.path


class Logger:
    __instance = None

    def __init__(self):
        self.__appname = "DelayBot"
        self.__logger = logging.getLogger(self.__appname)
        self.__logger.setLevel(logging.DEBUG)

        self.__base_dir = "./log"
        self.__log_file = "{0}/{1}.log".format(self.__base_dir, self.__appname)
        if not os.path.isfile(self.__log_file):
            os.makedirs(self.__base_dir)
            open(self.__log_file, 'w').close()
        # create file handler which logs even debug messages
        file_handler = logging.FileHandler(self.__log_file)
        file_handler.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add the handlers to the logger
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    @classmethod
    def g(cls):
        if Logger.__instance is None:
            Logger.__instance = Logger()
        return cls.__instance

    def get(self):
        return self.__logger

    @staticmethod
    def __format(*args):
        msg = ""
        for i in args:
            msg += str(i)
        return msg

    def info(self, *args):
        self.__logger.info(Logger.__format(*args))

    def debug(self, *args):
        self.__logger.debug(Logger.__format(*args))

    def warning(self, *args):
        self.__logger.warning(Logger.__format(*args))

    def error(self, *args):
        self.__logger.error(Logger.__format(*args))

    def critical(self, *args):
        self.__logger.critical(Logger.__format(*args))
