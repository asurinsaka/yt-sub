from sqlalchemy import Column, ForeignKey, String, Integer

from .database import Base


class PlayList(Base):
    __tablename__ = "playlist"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, index=True)


class Video(Base):
    __tablename__ = "video"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    upload_date = Column(Integer)
    url = Column(String, index=True)
    status = Column(String)
    location = Column(String)
    playlist_id = Column(String, ForeignKey("playlist.id"))

