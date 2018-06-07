from slacker import Slacker
import os


class Messenger:

    def __init__(self):
        # TODO: handle token better
        print("configuring messenger")
        self.SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
        self.slack = Slacker(self.SLACK_BOT_TOKEN)
        print("configured messenger")

    def post_message_to_channel(self, image):
        message = "I am {:.2%} sure this is the newest soup board: {}".format(image.soup_confidence, image.url)

        print(f"posting message to channel:\n\t {message}")

        self.slack.chat.post_message('#soup-bot', message, username="soup-bot")

        image.posted = 1

