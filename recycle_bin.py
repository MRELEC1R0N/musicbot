'''
#first code to run the musci

import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dlc import YoutubeDL



# Replace with your bot token
BOT_TOKEN = "MTEyODczMTEzMzY0Mzg2NjMxMg.GgfQS9.JBazvHEXHKHdPVI7z8OYDlc4d8ZAN3Ma8_q7pw"
class Song:
    def __init__(self, title, url, duration):
        self.title = title
        self.url = url
        self.duration = duration


client = commands.Bot(command_prefix="!",intents=discord.Intents.all())

# Music player initialization
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(title)s.%(ext)s',
}
ydl = YoutubeDL(ydl_opts)

# Queue for storing song requests
song_queue = []
current_song = None

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

@client.command()
async def play(ctx, *, url):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.author.voice.channel.connect()

    # Extract audio information
    info = ydl.extract_info(url, download=False)
    song = Song(info["title"], info["url"], info["duration"])

    # Add song to queue
    song_queue.append(song)

    # Check if playing
    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f":music_note: Added **{song.title}** to the queue!")

@client.command()
async def queue(ctx):
    if not song_queue:
        await ctx.send("The queue is empty.")
    else:
        message = "Currently playing: " + current_song.title + "\n\nQueue:\n"
        for i, song in enumerate(song_queue):
            message += f"{i+1}. {song.title}\n"
        await ctx.send(message)

@client.command()
async def skip(ctx):
    if song_queue:
        song_queue.pop(0)
        await play_next(ctx)

@client.command()
async def stop(ctx):
    song_queue.clear()
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    await ctx.send(":stop_button: Stopped playback.")

async def play_next(ctx):
    if song_queue:
        current_song = song_queue.pop(0)
        source = discord.FFmpegPCMAudio(current_song.url)
        player = ctx.voice_client.play(source)
        await ctx.send(f":musical_note: Now playing: **{current_song.title}**")
@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()



client.run(BOT_TOKEN)

'''