from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from discord import FFmpegPCMAudio
from youtube_dlc import YoutubeDL
from extra_funtions import measure_time

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = bot.song_queue
        

    @commands.command()
    async def join(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command(name="play", help="Plays a song from YouTube.")
    @measure_time
    async def play_song(self, ctx, url):
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "lxml")

            artist_tag = soup.find("meta", {"property": "og:music:artist"})
            title_tag = soup.find("meta", {"property": "og:title"})
            album_tag = soup.find("meta", {"property": "og:music:album"})

            artist = artist_tag.attrs["content"] if artist_tag else None
            title = title_tag.attrs["content"] if title_tag else None
            album = album_tag.attrs["content"] if album_tag else None

        except Exception as e:
            await ctx.send(f"Error extracting song information: {e}")
            return

        try:
            search_query = f"{artist} - {title}" + (f" - {album}" if album else "")

            with YoutubeDL({"format": "bestaudio/best", "noplaylist": True}) as ydl:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                if "formats" in info["entries"][0]:
                    audio_url = info["entries"][0]["formats"][0]["url"]
                else:
                    await ctx.send("Could not find a suitable audio format for this video.")
                    return

            if ctx.author.voice and ctx.author.voice.channel:
                if not ctx.voice_client or not ctx.voice_client.is_connected():
                    await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                return

            if not ctx.voice_client.is_playing():
                ctx.voice_client.play(FFmpegPCMAudio(audio_url), after=self.play_next_song)
                await ctx.send(f"Now playing: {info['entries'][0]['title']}")
            else:
                self.song_queue.append(audio_url)
                await ctx.send(f"Song added to queue.")

        except Exception as e:
            await ctx.send(f"Error playing song: {e}")
    def play_next_song(self, error=None):
        if error:
            print(f"Player error: {error}")
        if self.song_queue:
            next_song = self.song_queue.pop(0)  # Songs are removed from the queue here
            self.bot.voice_clients[0].play(FFmpegPCMAudio(next_song), after=self.play_next_song)




async def setup(bot):
    await bot.add_cog(Music(bot))