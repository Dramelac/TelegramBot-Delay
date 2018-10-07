from flask import Flask

from Bot import Bot

# PRod app - webhook messages

app = Flask(__name__)


def init():
    global bot
    bot = Bot()


@app.route('/webhook')
def webhook():
    # TODO setup webhook
    return ""


init()
if __name__ == '__main__':
    app.run()
