#!/usr/bin/python3
import time
import traceback

from requests.exceptions import ConnectionError

from Bot import Bot
from Logger import logger

# Dev app - pooling messages

if __name__ == '__main__':
    bot = Bot()
    try:
        while True:
            try:
                bot.pool_message()
            except ConnectionError:
                pass
            except Exception as e:
                logger.critical("FATAL ERROR ! Crash handle :\n", traceback.format_exc())
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Exiting")
