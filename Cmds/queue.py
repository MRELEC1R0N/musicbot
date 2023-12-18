from discord.ext import commands
import random

class QueueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = bot.song_queue

    @commands.command(name="view_queue", help="Displays the current song queue.")
    async def view_queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is currently empty.")
        else:
            await ctx.send("Here's the current song queue:\n" + "\n".join(self.song_queue))

    # @commands.command(name="skip", help="Skips the current song.")
    # async def skip(self, ctx):
    #     if ctx.voice_client.is_playing():
    #         ctx.voice_client.stop()

    @commands.command(name="clear_queue", help="Clears the song queue.")
    async def clear_queue(self, ctx):
        self.song_queue.clear()
        await ctx.send("The song queue has been cleared.")

    @commands.command(name="remove", help="Removes a specific song from the queue.")
    async def remove_song(self, ctx, index: int):
        try:
            removed_song = self.song_queue.pop(index - 1)
            await ctx.send(f"Removed song {index} from the queue.")
        except IndexError:
            await ctx.send("Invalid index.")

    @commands.command(name="shuffle", help="Shuffles the song queue.")
    async def shuffle_queue(self, ctx):
        random.shuffle(self.song_queue)
        await ctx.send("Shuffled the song queue.")

    @commands.command(name="move", help="Moves a song in the queue.")
    async def move_song(self, ctx, from_index: int, to_index: int):
        try:
            song = self.song_queue.pop(from_index - 1)
            self.song_queue.insert(to_index - 1, song)
            await ctx.send(f"Moved song {from_index} to position {to_index} in the queue.")
        except IndexError:
            await ctx.send("Invalid index.")


def setup(bot):
    bot.add_cog(QueueCommands(bot))