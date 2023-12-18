import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dlc import YoutubeDL
import settings
import tracemalloc
from db import Database


logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.all()
    # intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.song_queue = []
    bot.db = Database(settings.database_key, "Music")

    # Load all cogs on bot ready
    async def load_cogs():
        for cog_file in settings.CMDS_DIR.glob("*.py"):
            if cog_file.is_file():
                bot.load_extension(f"Cmds.{cog_file.stem}")
                logger.info(f"Loaded {cog_file.stem}")

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await load_cogs()

    for cmd in ['load', 'unload', 'reload']:
        @bot.command(name=  cmd)
        async def _cmd(ctx, cog: str):
            try:
                getattr(bot, f'{cmd}_extension')(f"Cmds.{cog.lower()}")
                await ctx.send(f'Done {cmd}ing')
            except Exception as e:
                await ctx.send(f'Error: {e}')


    tracemalloc.start()
    bot.run(settings.Discord_api)


if __name__ == "__main__":
    run()