try:
    import unzip_requirements
except ImportError:
    pass

import os
import classifier
from datetime import datetime
from instalooter.looters import ProfileLooter
from queries import Queries
from messenger import Messenger
from entities import *
import fs

queries = Queries()

def classify_posts(posts):
    with classifier.Classifier() as c:
        for post in posts:
            timestamp = post['taken_at_timestamp']
            picture_url = post['display_url']

            print(f"checking url {picture_url}")

            if queries.image_exists(picture_url):
                print(f"\talready processed. skipping {picture_url}")
                continue

            print(f"\timage not loaded, adding to db {picture_url}")

            image = Image(url=picture_url, post_date=timestamp)

            print(f"\tclassifying image {picture_url}")
            c.classify(image)
            queries.add(image)

    queries.commit()


def update(event, context):
    start_time = datetime.now()

    print("Starting soup")

    queries = Queries()

    print("configuring looter")
    # https://github.com/althonos/InstaLooter/issues/173
    ProfileLooter._cachefs = fs.open_fs("osfs:///tmp/")
    looter = ProfileLooter("davesfreshpasta")
    print("configured looter")

    print("finished setup")

    last_date = queries.most_recent_image_date()
    timeframe = (start_time.date(), last_date)
    print(f"last post date: {last_date}. Timeframe is {timeframe}")

    posts = looter.medias(timeframe=timeframe)

    if posts:
        classify_posts(posts)

    repost_soup = os.environ.get("REPOST_SOUP", default=False)
    confidence = os.environ.get("CONFIDENCE", default=0.8)

    # TODO: move posting into post iteration loop
    top_image = queries.top_soup(confidence)

    if (not top_image.posted) or repost_soup:
        messenger = Messenger()
        messenger.post_message_to_channel(top_image)
        queries.commit() # messenger will mark image as posted

    elapsed_time = datetime.now() - start_time
    print(f"Finished soup. Elapsed time {elapsed_time}")


if __name__ == '__main__':
    update(None, None)
