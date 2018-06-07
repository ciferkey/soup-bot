import os
from instalooter.looters import ProfileLooter
import classifier
from entities import *
from datetime import datetime
from queries import Queries

photo_path = "C://Users//mbrunelle//soup//photos"

os.makedirs(photo_path, exist_ok=True)
os.makedirs(photo_path + "/probably_not_soup", exist_ok=True)
os.makedirs(photo_path + "/probably_soup", exist_ok=True)

queries = Queries()

print("configuring looter")
# https://github.com/althonos/InstaLooter/issues/173
looter = ProfileLooter("davesfreshpasta")
print("configured looter")

start_time = datetime.now()

last_date = queries.oldest_image_date()
timeframe = (start_time.date(), last_date)

posts = looter.medias(timeframe)

# https://github.com/althonos/InstaLooter/issues/171
try:
    with classifier.Classifier() as c:
        for post in posts:
            url = post['display_url']

            if queries.image_exists(url):
                print(f"\talready classified, skipping {url}")
                continue

            timestamp = post['taken_at_timestamp']
            print(url)
            image = Image(url=url, post_date=timestamp)
            c.classify(image)
            queries.add(image)

            destination = photo_path + "/probably_not_soup/"
            if image.soup_confidence >= 0.7:
                # Get file name without path stripped
                destination = photo_path + "/probably_soup/"

            file_name = image.file_name().split("/")[-1]

            print("\t" + destination + file_name)
            try:
                os.rename(image.file_name(), destination + file_name)
            except FileExistsError:
                print(f"\talready exists, skipping")
            queries.commit()
except RuntimeError as err:
    print(err)