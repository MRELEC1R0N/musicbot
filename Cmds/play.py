from discord.ext import commands
from discord import FFmpegPCMAudio, ButtonStyle, InteractionType
from discord.ui import Button, View
from extra_funtions import measure_time
from discord import Embed
from songs_info import get_song_info
import asyncio





class SkipButton(Button):
    def __init__(self, cog):
        super().__init__(style=ButtonStyle.primary, label="Skip")
        self.cog = cog

    async def callback(self, interaction):
        await self.cog.skip_song(interaction)

class MusicView(View):
    def __init__(self, cog):
        super().__init__()
        self.add_item(SkipButton(cog))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = bot.song_queue
        self.view = MusicView(self)
        self.collection = bot.db.get_collection("song_history")
        self.ctx = None  # Add this line


    @commands.command()
    async def join(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command(name="play", help="Plays a song from YouTube.")
    @measure_time
    async def play_song(self, ctx,url):
        if ctx.author.voice and ctx.author.voice.channel:
                    '''checking if user is connected or not'''
                    if not ctx.voice_client or not ctx.voice_client.is_connected():
                        await ctx.author.voice.channel.connect()

        else:
                    await ctx.send("You are not connected to a voice channel.")
                    return
        
        #getting the song info
        audio_url, title, artist,album,info = await get_song_info(url)

        if not ctx.voice_client.is_playing():
                ctx.voice_client.play(FFmpegPCMAudio(audio_url,before_options="-ss 00:00:05"), after=self.play_next_song)
                
                if 'entries' in info:
                    title = info['entries'][0]['title']
                else:
                    title = info['title']

                embed = Embed(title="Now Playing", description=title, color=0x00ff00)
                embed.add_field(name="Artist", value=artist, inline=True)
                embed.add_field(name="Album", value=album, inline=True)
                if 'entries' in info:
                    thumbnail_url = info['entries'][0]['thumbnails'][0]['url']
                else:
                    thumbnail_url = info['thumbnails'][0]['url']

                embed.set_thumbnail(url=thumbnail_url)
                await ctx.send(embed=embed, view=self.view)
                # song_history = {
                #             "user_id": ctx.author.id,
                #             "song_title": title,
                #             "song_artist": artist,
                #             "song_album": album,
                #             "song_url": audio_url
                #             }
                # self.collection.insert_one(song_history)

        else:
                # self.song_queue.append(audio_url)

                song_queue_item = {
                    "audio_url": audio_url,
                    "title": title,
                    "artist": artist,
                    "album": album
                            }

                self.song_queue.append(song_queue_item)
                await ctx.send(f"Song added to queue.", view=self.view)
                self.collection.update_one(
                    {"user_id": ctx.author.id},
                    {"$push": {"song_queue": song_queue_item}},
                    upsert=True
                                )



    @commands.command(name="queue", help="Adds a song to the queue.")
    async def queue_song(self, ctx, url):
        audio_url, title, artist, album = await get_song_info(url)

        song_queue_item = {
            "audio_url": audio_url,
            "title": title,
            "artist": artist,
            "album": album
        }

        self.song_queue.append(song_queue_item)
        await ctx.send(f"Song '{title}' added to queue.", view=self.view)

        self.collection.update_one(
            {"user_id": ctx.author.id},
            {"$push": {"song_queue": song_queue_item}},
            upsert=True
        )
    @commands.command(name="skip", help="Skips the currently playing song.")
    async def skip_song(self, ctx):
        if isinstance(ctx, commands.Context):
            voice_client = ctx.voice_client
            send = ctx.send
        else:  # ctx is an InteractionContext
            voice_client = self.bot.get_guild(ctx.guild_id).voice_client
            send = ctx.response.send_message

        if voice_client.is_playing():
            voice_client.stop()
            await send("Skipped the current song.")
            await self.play_next_song(ctx)
        else:
            await send("No song is currently playing.")
        

    def after_callback(self, error):    
        coro = self.play_next_song(self.ctx)  # Use self.ctx here
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            fut.result()
        except:
            # an error happened in play_next_song
            pass

    async def play_next_song(self, ctx):
        if self.song_queue:
            next_song = self.song_queue.pop(0)
            user_id = ctx.author.id if isinstance(ctx, commands.Context) else ctx.user.id
            user_document = self.collection.find_one({"user_id": user_id})
            if user_document and "song_queue" in user_document:
                self.collection.update_one(
                    {"user_id": user_id},
                    {"$pop": {"song_queue": -1}}
                )
            voice_client = ctx.voice_client if isinstance(ctx, commands.Context) else self.bot.get_guild(ctx.guild_id).voice_client
            voice_client.play(FFmpegPCMAudio(next_song['audio_url'], before_options="-ss 00:00:05"), after=self.after_callback)
def setup(bot):
    bot.add_cog(Music(bot))