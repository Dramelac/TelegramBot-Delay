import time

from Bot import Bot

# Dev app - pooling messages


if __name__ == '__main__':
    bot = Bot()
    try:
        while True:
            try:
                bot.pool_message()
            except Exception as e:
                print("[ERROR] FATAL ERROR ! Crash handle : ", e)
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exiting")
