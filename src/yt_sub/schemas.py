from pydantic import BaseModel


class URLItem(BaseModel):
    url: str


class Video(BaseModel):
    id: str | None = None
    title: str | None = None
    url: str | None = None
    status: str
    location: str | None = None
    playlist_id: str | None = None
    upload_date: int | None = None
