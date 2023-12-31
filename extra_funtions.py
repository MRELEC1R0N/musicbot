'''
In this section of code i have stored the extra funtions used by the commands of the bot to delever a good quality musci.
'''


import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        await args[1].send(f"Command executed in {elapsed_time} seconds.")
        return result
    return wrapper
















# import re
# def recognize_platform(url):
#   """
#   Function to identify the platform from a given URL.

#   Args:
#     url: The URL to be analyzed.

#   Returns:
#     A string representing the identified platform, or None if platform cannot be determined.
#   """

#   youtube_regex = r"^(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=)?([^&]+)"
#   spotify_regex = r"^(?:https?://)?open\.spotify\.com/track/([^?]+)"
#   soundcloud_regex = r"^(?:https?://)?(?:www\.)?soundcloud\.com/([^/]+)/([^?]+)"
#   apple_music_regex = r"^(?:https?://)?(?:www\.)?music\.apple\.com/us/album/([^/]+)/([^?]+)"
#   twitch_regex = r"^(?:https?://)?(?:www\.)?twitch\.tv/videos/([^?]+)"

#   match = re.match(youtube_regex, url)
#   if match:
#     return "youtube"
#   match = re.match(spotify_regex, url)
#   if match:
#     return "spotify"
#   match = re.match(soundcloud_regex, url)
#   if match:
#     return "soundcloud"
#   match = re.match(apple_music_regex, url)
#   if match:
#     return "apple_music"
#   match = re.match(twitch_regex, url)
#   if match:
#     return "twitch"

#   return None


