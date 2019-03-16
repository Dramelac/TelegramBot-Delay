import time
import traceback

from Bot import Bot
# Dev app - pooling messages
from Logger import Logger

if __name__ == '__main__':
    bot = Bot()
    try:
        while True:
            try:
                bot.pool_message()
            except Exception as e:
                Logger.g().critical("FATAL ERROR ! Crash handle :\n", traceback.format_exc())
            time.sleep(2)
    except KeyboardInterrupt:
        Logger.g().info("Exiting")
