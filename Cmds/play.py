from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from discord import FFmpegPCMAudio
from youtube_dlc import YoutubeDL

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def join(self,ctx):
        channel = ctx.author.voice.channel
        await channel.connect()


    @commands.command(name="play", help="Plays a song from YouTube.")
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

            with YoutubeDL({"format": "bestaudio/best"}) as ydl:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                video_id = info["entries"][0]["id"]
                audio_url = info["entries"][0]["formats"][0]["url"]

            voice = await ctx.message.author.voice.channel.connect()
            player = voice.play(FFmpegPCMAudio(audio_url))

            await ctx.send(f"Now playing: {info['entries'][0]['title']}")

        except Exception as e:
            await ctx.send(f"Error playing song: {e}")

async def setup(bot):
    await bot.add_cog(Music(bot))