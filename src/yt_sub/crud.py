from typing import Optional, List, Type

import yt_dlp
from . import models
from sqlalchemy.orm import Session

from . import schemas


def get_playlists(db: Session) -> list[Type[models.PlayList]]:
    return db.query(models.PlayList).all()


def create_playlist(db: Session, url: str):
    info = request_playlist_info(url)
    playlist = models.PlayList(
        id=info["id"],
        title=info["title"],
        url=info["webpage_url"],
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


def request_playlist_info(url: str, total_videos: int = 0) -> models.PlayList:
    ydl_opts = {"playlistend": total_videos, "ignoreerrors": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    info['entries'] = [i for i in info['entries'] if i is not None]
    return info


def get_playlist_by_url(db: Session, url: str):
    return db.query(models.PlayList).filter(models.PlayList.url == url).first()


def get_playlist_by_id(db: Session, list_id: str) -> models.PlayList:
    return db.query(models.PlayList).get(list_id)


def get_video_info_from_playlist(db: Session, list_id: str):
    playlist = get_playlist_by_id(db, list_id)
    playlist_info = request_playlist_info(playlist.url, 10)
    res = []
    for video_info in playlist_info['entries']:
        video = db.query(models.Video).get(video_info['id'])
        if video:
            res.append(video)
            continue
        video = models.Video(
            id=video_info['id'],
            title=video_info['title'],
            url=video_info['webpage_url'],
            status="not_downloaded",
            playlist_id=playlist.id,
            upload_date=int(video_info['upload_date'])
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        res.append(video)
    return res


def get_video_by_id(db: Session, video_id: str):
    return db.query(models.Video).get(video_id)


def update_video(db: Session, video_id: str, video: schemas.Video):
    video_entry = db.query(models.Video).get(video_id)
    for field in video.model_fields.keys():
        value = getattr(video, field)
        if value:
            setattr(video_entry, field, value)
    db.add(video_entry)
    db.commit()
    db.refresh(video_entry)
    return video_entry


def get_videos(db: Session, status: Optional[str] = None):
    query = db.query(models.Video)
    if status:
        query = query.filter(models.Video.status == status)
    return query.all()