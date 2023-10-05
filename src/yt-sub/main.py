from urllib import parse
from multiprocessing import Process

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, SessionLocal
from bin.downloader import download_videos


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/playlist/{playlist_id}")
async def get_playlist(playlist_id: str, db: Session = Depends(get_db)):
    play_list = crud.get_playlist_by_id(db, playlist_id)
    if play_list is None:
        raise HTTPException(status_code=404, detail="Play List not found")
    return play_list


@app.post("/playlist/")
async def create_playlist(url_item: schemas.URLItem, db: Session = Depends(get_db)):
    url = url_item.url
    parsed = parse.urlparse(url)
    params = parse.parse_qsl(parsed.query)
    list_id = dict(params).get("list")
    playlist = crud.get_playlist_by_url(db, url)
    if playlist is None and list_id:
        playlist = crud.get_playlist_by_id(db, list_id)
    if playlist:
        raise HTTPException(status_code=400, detail="Play list already exist.")
    return crud.create_playlist(db, url)


@app.post("/playlist/{playlist_id}/get_videos/")
async def get_videos_for_playlist(playlist_id: str, db: Session = Depends(get_db)):
    videos = crud.get_video_info_from_playlist(db, playlist_id)
    return videos


@app.put("/video/{video_id}/", response_model=schemas.Video)
async def update_video(video_id: str, video_item: schemas.Video, db: Session = Depends(get_db)):
    video = crud.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    updated = crud.update_video(db, video_id, video_item)
    return updated


@app.get('/videos')
async def get_videos(status: str, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, status)
    return videos


def start_downloader():
    p = Process(target=download_videos, daemon=True)
    p.start()


# if os.getenv("START_DOWNLOADER", 'False').lower() == 'true':
start_downloader()
