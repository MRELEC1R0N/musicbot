from discord.ext import commands
from discord import FFmpegPCMAudio, ButtonStyle, InteractionType
from discord.ui import Button, View
from extra_funtions import measure_time
from discord import Embed
from songs import get_song_info
import asyncio
from music_ui import MusicView, NowPlayingView 





class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = bot.song_queue
        self.view = MusicView(self)
        self.collection = bot.db.get_collection("song_history")
        self.ctx = None  # Add this line



    async def play_audio(self, ctx, song_info):
        voice_client = ctx.voice_client if isinstance(ctx, commands.Context) else self.bot.get_guild(ctx.guild_id).voice_client
        voice_client.play(FFmpegPCMAudio(song_info['audio_url'], before_options="-ss 00:00:05"), after=self.after_callback)
        now_playing_view = NowPlayingView(song_info)
        if isinstance(ctx, commands.Context):
            await ctx.send(content=f"Now playing: {song_info['title']} by {song_info['artist']} from the album {song_info['album']}", view=now_playing_view)
        else:  # ctx is an InteractionContext
            await ctx.response.send_message(content=f"Now playing: {song_info['title']} by {song_info['artist']} from the album {song_info['album']}", view=now_playing_view)



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
        audio_url, title, artist,album = await get_song_info(url)

        song_queue_item = {
            "audio_url": audio_url,
            "title": title,
            "artist": artist,
            "album": album
        }
        if not ctx.voice_client.is_playing():
            await self.play_audio(ctx,song_queue_item)
        else:
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
            send = ctx.response.send_message if not ctx.response.is_done() else lambda x: None

        message = ""
        if voice_client.is_playing():
            voice_client.stop()
            message = "Skipped the current song."
            if self.song_queue:
                next_song = self.song_queue.pop(0)
                await self.play_audio(ctx, next_song)
        else:
            message = "No song is currently playing."
        await send(message)


    def after_callback(self, error):    
        coro = self.play_next_song(self.ctx)  # Use self.ctx here
        if not self.bot.loop.is_closed():
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
            await self.play_audio(ctx, next_song)
            
            
def setup(bot):
    bot.add_cog(Music(bot))