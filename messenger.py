from slacker import Slacker
import os
from datetime import datetime


class Messenger:

    def __init__(self):
        # TODO: handle token better
        print("configuring messenger")
        self.SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
        self.slack = Slacker(self.SLACK_BOT_TOKEN)
        print("configured messenger")

    def post_message_to_channel(self, image):

        message_template = "I am {:.2%} sure this is the newest specials board: {}"


        current_date = datetime.now().date()
        date = datetime.fromtimestamp(image.post_date).date()

        if (date != current_date):
            message_template = "I am {:.2%} sure this is the most recent specials board, however it was posted on " \
                               + str(date) + " : {}"

        message = message_template.format(image.soup_confidence, image.url)

        print(f"posting message to channel:\n\t {message}")

        self.slack.chat.post_message('#soup-bot', message, username="soup-bot")

        image.posted = 1

