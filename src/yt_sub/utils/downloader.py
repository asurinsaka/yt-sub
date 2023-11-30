#!/usr/utils/env python3
import logging
import os
import time
from pathlib import Path

import requests
import yt_dlp

BASE_URL = os.getenv('BASE_URL', "http://localhost:8000")
DATA_DIR = Path(os.getenv("DATA_DIR", "../../../data"))

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(LOGLEVEL)


class UpdateVideoEntry(yt_dlp.postprocessor.PostProcessor):

    def update_video_entry(self, file_info):
        video_meta = {}
        video_meta['status'] = 'downloaded'
        video_meta['location'] = file_info["filename"]
        res = requests.put(
            BASE_URL + f'/video/{file_info["id"]}',
            json=video_meta,
        )
        return res

    def run(self, file_info):
        self.to_screen('Update video entry')
        self.update_video_entry(file_info)
        return [], file_info


def get_playlist_title(video):
    res = requests.get(f"{BASE_URL}/playlist/{video['playlist_id']}")
    playlist = res.json()
    return playlist['title']


def download(video):
    playlist_title = get_playlist_title(video)
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'paths': {'home': str(DATA_DIR / playlist_title)},
        'outtmpl': "%(upload_date)s_%(title).10s.%(ext)s"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(UpdateVideoEntry(), when='post_process')
        error_code = ydl.download(video.get('url'))


def download_videos():
    while True:
        res = requests.get(BASE_URL + '/videos?status=download')
        videos = res.json()

        if not videos:
            logger.info("No video to download, sleeping")
            time.sleep(30)
            continue
        for video in videos:
            logger.info(f"Download video {video['title']}")
            download(video)


if __name__ == '__main__':
    download_videos()
