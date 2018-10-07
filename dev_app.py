from Bot import Bot
import time

# Dev app - pooling messages


if __name__ == '__main__':
    bot = Bot()
    try:
        while True:
            bot.pool_message()
            time.sleep(3)
    except KeyboardInterrupt:
        print("Exiting")
