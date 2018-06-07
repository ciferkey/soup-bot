import os
from sqlalchemy.orm import *
from entities import *
from datetime import datetime, timedelta


class Queries:
    """
    Contains the database queries
    """

    def __init__(self):
        """
        Based on environment variables will load either PostgreSQL on RDS or a local SQLite instance.

        Creates all schema if it has not been initialized yet.
        """
        print("Initializing query engine.")
        if os.environ.get("ENV", None) == "AWS":
            print("Connecting to postgres database on AWS")
            rds_user = os.environ.get("RDS_USER")
            rds_password = os.environ.get("RDS_PASSWORD")
            rds_port = os.environ.get("RDS_PORT", 5432)
            rds_host = os.environ.get("RDS_HOST")

            url = f'postgresql://{rds_user}:{rds_password}@{rds_host}:{rds_port}/soup'

            self.engine = create_engine(url)
            print("Connected to postgres database on AWS")
            # Do I actually... miss DI?
        else:
            print("Connecting to local sqlite database")
            self.engine = create_engine('sqlite:///resources/soup.db')
            print("Connecting to local sqlite database")
        print("Creating Schema if necessary.")
        Base.metadata.create_all(self.engine)
        print("Creating session")
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print("Finished initializing query engine")

    def image_exists(self, url):
        """
        Indicates whether an image exists alreaday for the given url

        :param the image to search
        :return:
        """
        return self.session.query(exists().where(Image.url == url)).scalar()

    def top_soup(self, confidence=0.8):
        """
        Finds the most recent classification that is likely soup.
        :return:
        """
        return self.session.query(Image)\
            .filter(Image.soup_confidence >= confidence)\
            .order_by(desc(Image.post_date))\
            .first()

    def most_recent_image_date(self):
        """
        Finds the date of the most recent image.
        :return:
        """
        image = self.session.query(Image)\
            .order_by(desc(Image.post_date))\
            .first()

        if not image:
            return datetime.now().date() - timedelta(days=5)

        return datetime.fromtimestamp(image.post_date).date()

    def oldest_image_date(self):
        """
        Finds the date of the oldest image.
        :return:
        """
        image = self.session.query(Image)\
            .order_by(asc(Image.post_date))\
            .first()

        if not image:
            return datetime.now().date() - timedelta(days=5)

        return datetime.fromtimestamp(image.post_date).date()

    def add(self, entry):
        """
        I should likely refactor this.
        :param entry: the entry to add
        :return:
        """
        self.session.add(entry)

    # TODO consider making queries managed with a with statement and auto commit
    def commit(self):
        """
        I should likely refactor this.
        :return:
        """
        self.session.commit()
