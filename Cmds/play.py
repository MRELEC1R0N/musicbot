from discord.ext import commands
from discord import FFmpegPCMAudio, ButtonStyle, InteractionType
from discord.ui import Button, View
from bs4 import BeautifulSoup
import requests
from youtube_dlc import YoutubeDL
from extra_funtions import measure_time
from discord import Embed
from urllib.parse import urlparse




class SkipButton(Button):
    def __init__(self, cog):
        super().__init__(style=ButtonStyle.primary, label="Skip")
        self.cog = cog

    async def callback(self, interaction):
        if self.cog.song_queue:
            self.cog.play_next_song()
            await interaction.response.send_message("Skipped to the next song.", ephemeral=True)
        else:
            await interaction.response.send_message("No more songs in the queue.", ephemeral=True)

class MusicView(View):
    def __init__(self, cog):
        super().__init__()
        self.add_item(SkipButton(cog))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = bot.song_queue
        self.view = MusicView(self)

    @commands.command()
    async def join(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command(name="play", help="Plays a song from YouTube.")
    @measure_time
    async def play_song(self, ctx,url):
        parsed_url = urlparse(url)
        artist = None
        title = None
        album = None

            
        if ctx.author.voice and ctx.author.voice.channel:
                    '''checking if user is connected or not'''
                    if not ctx.voice_client or not ctx.voice_client.is_connected():
                        await ctx.author.voice.channel.connect()

        else:
                    await ctx.send("You are not connected to a voice channel.")
                    return
            

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
                await ctx.send(f"Error playing song: {e}")


    


            if not ctx.voice_client.is_playing():
                ctx.voice_client.play(FFmpegPCMAudio(audio_url,before_options="-ss 00:00:05"), after=self.play_next_song)

                embed = Embed(title="Now Playing", description=f"{info['entries'][0]['title']}", color=0x00ff00)
                embed.add_field(name="Artist", value=artist, inline=True)
                embed.add_field(name="Album", value=album, inline=True)
                embed.set_thumbnail(url=info['entries'][0]['thumbnails'][0]['url'])
                await ctx.send(embed=embed, view=self.view)

            else:
                self.song_queue.append(audio_url)
                await ctx.send(f"Song added to queue.", view=self.view)

    def play_next_song(self, error=None):
        if error:
            print(f"Player error: {error}")
        if self.song_queue:
            next_song = self.song_queue.pop(0)  # Songs are removed from the queue here
            self.bot.voice_clients[0].play(FFmpegPCMAudio(next_song), after=self.play_next_song)

def setup(bot):
    bot.add_cog(Music(bot))