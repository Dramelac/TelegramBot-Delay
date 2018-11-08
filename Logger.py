import logging


class Logger:
    __instance = None

    def __init__(self):
        self.__appname = "delayboy"
        self.__logger = logging.getLogger(self.__appname)
        self.__logger.setLevel(logging.DEBUG)

        self.__base_dir = "."
        # create file handler which logs even debug messages
        file_handler = logging.FileHandler("{0}/{1}.log".format(self.__base_dir, self.__appname))
        file_handler.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add the handlers to the logger
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    def __del__(self):
        pass

    @classmethod
    def get_logger(cls):
        return cls.__instance

    def info(self, log):
        pass

    def error(self, log):
        pass

    def custom(self, category, log):
        pass
