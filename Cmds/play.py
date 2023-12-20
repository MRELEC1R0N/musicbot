# play.py
from extra_funtions import measure_time
from discord.ext import commands
from music_utils import (
    join,
    queue_song,
    play_song as  play_song_util,
    pause_song,
    resume_song,
    skip_song,
    leave
)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = bot.song_queue
        self.collection = bot.db.get_collection("song_history")
        self.ctx = None  # Add this line

    # ... (other code)

    @commands.command(name="join")
    async def join(self, ctx):
        await join(ctx)

    @commands.command(name="queue", help="Adds a song to the queue.")
    async def queue_song(self, ctx, url):
        await queue_song(ctx, url)

    @commands.command(name="play", help="Plays a song from YouTube.")
    @measure_time
    async def play_song(self, ctx, url):
        await play_song_util(ctx, url)
        
    @commands.command(name="pause", help="Pauses the currently playing song.")
    async def pause_song(self, ctx):
        await pause_song(ctx)

    @commands.command(name="resume", help="Resumes the paused song.")
    async def resume_song(self, ctx):
        await resume_song(ctx)

    @commands.command(name="skip", help="Skips the currently playing song.")
    async def skip_song(self, ctx):
        await skip_song(ctx)

    @commands.command(name="leave", help="Leaves the voice channel.")
    async def leave(self, ctx):
        await leave(ctx)

    # ... (other code)

def setup(bot):
    bot.add_cog(Music(bot))
