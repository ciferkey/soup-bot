from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

"""
Models used for storing the image classifications.
"""

Base = declarative_base()


class Image(Base):
    """
    Holds the image data from a scraped post and the classification from tensorflow
    """
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(TEXT(300))
    post_date = Column(Integer)
    soup_confidence = Column(Float)
    posted = Column(Integer, default=0)

    def file_name(self):
        return "/tmp/" + self.url.split('/')[-1]

