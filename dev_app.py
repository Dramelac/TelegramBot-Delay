import time

from Bot import Bot

# Dev app - pooling messages


if __name__ == '__main__':
    bot = Bot()
    try:
        while True:
            bot.pool_message()
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exiting")
