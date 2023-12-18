from discord.ext import commands
from db import Database

class UserProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_info = bot.db.get_collection('Users_info')

    @commands.command(name="register", help="Registers a new user.")
    async def register(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name
        if self.users_info.find_one({"_id": user_id}):
            await ctx.send("You're already registered!")
        else:
            self.users_info.insert_one({"_id": user_id, "username": username, "songs_played": [], "saved_playlists": []})
            await ctx.send("You've been registered!")

async def setup(bot):
    await bot.add_cog(UserProfile(bot))