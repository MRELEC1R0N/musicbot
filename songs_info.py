# song_info.py

from urllib.parse import urlparse
from youtube_dlc import YoutubeDL
import requests
from bs4 import BeautifulSoup

class SongInfoError(Exception):
    pass

async def get_song_info(url):
    parsed_url = urlparse(url)
    artist = None
    title = None
    album = None

    if "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc:
        # Handle YouTube URLs
        with YoutubeDL({"format": "bestaudio/best", "noplaylist": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['formats'][0]['url']
            title = info['title']

    else:
        # Handle non-YouTube URLs (e.g., Spotify)
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "lxml")

            artist_tag = soup.find("meta", {"property": "og:music:artist"})
            title_tag = soup.find("meta", {"property": "og:title"})
            album_tag = soup.find("meta", {"property": "og:music:album"})

            artist = artist_tag.attrs["content"] if artist_tag else None
            title = title_tag.attrs["content"] if title_tag else None
            album = album_tag.attrs["content"] if album_tag else None

            search_query = f"{artist} - {title}" + (f" - {album}" if album else "")

            with YoutubeDL({"format": "bestaudio/best", "noplaylist": True}) as ydl:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                audio_url = info['entries'][0]['formats'][0]['url']

        except Exception as e:
            raise SongInfoError(f"Error getting song info: {e}")

    return audio_url, title, artist, album,info