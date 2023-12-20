# music_utils.py


from discord import FFmpegPCMAudio
from songs import get_song_info
from songs import get_song_info  # Assuming this function is defined in songs.py
from discord.ext import commands
from discord.ext.commands import Bot, Context
from songs import get_song_info as play_audio
from discord import FFmpegPCMAudio
from youtube_dlc import YoutubeDL
from discord import Embed


async def after_callback(ctx):
    # Check if there are more songs in the queue
    if ctx.bot.song_queue:
        # Get the next song
        next_song = ctx.bot.song_queue.pop(0)

        # Play the next song
        await play_song(ctx, next_song["audio_url"])
    else:
        # No more songs in the queue, disconnect from the voice channel
        await ctx.voice_client.disconnect()


def get_audio_url_from_youtube_url(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['formats'][0]['url']
    return audio_url

async def play_song(ctx, url):
    # Get the voice client for the guild
    voice_client = ctx.voice_client if isinstance(ctx, commands.Context) else ctx.bot.get_guild(ctx.guild_id).voice_client

    # If the bot is not connected to a voice channel, join the author's voice channel
    if voice_client is None:
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel
        voice_client = await channel.connect()

    # Get the audio URL and song info
    audio_url, title, artist, album = await get_song_info(url)

    # Create an FFmpegPCMAudio source
    audio_source = FFmpegPCMAudio(audio_url)

    # Play the audio
    voice_client.play(audio_source)

    # Send a message to the channel with the song info
    await ctx.send(f"Now playing: {title} by {artist}" + (f" from {album}" if album else ""))



    
async def join(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        channel = ctx.author.voice.channel
        await channel.connect()

async def queue_song(ctx, url):
    audio_url, title, artist, album = await get_song_info(url)

    song_queue_item = {
        "audio_url": audio_url,
        "title": title,
        "artist": artist,
        "album": album
    }

    ctx.bot.song_queue.append(song_queue_item)
    await ctx.send(f"Song '{title}' added to queue.", view=ctx.bot.music.view)

    ctx.bot.collection.update_one(
        {"user_id": ctx.author.id},
        {"$push": {"song_queue": song_queue_item}},
        upsert=True
    )

async def pause_song(ctx):
    voice_client = ctx.voice_client if isinstance(ctx, Context) else ctx.bot.get_guild(ctx.guild_id).voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused the current song.")
    else:
        await ctx.send("No song is currently playing.")

async def resume_song(ctx):
    voice_client = ctx.voice_client if isinstance(ctx, Context) else ctx.bot.get_guild(ctx.guild_id).voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed the song.")
    else:
        await ctx.send("No song is currently paused.")

async def skip_song(ctx):
    if isinstance(ctx, Context):
        voice_client = ctx.voice_client
        send = ctx.send
    else:  # ctx is an InteractionContext
        voice_client = ctx.bot.get_guild(ctx.guild_id).voice_client
        send = ctx.response.send_message if not ctx.response.is_done() else lambda x: None

    message = ""
    if voice_client.is_playing():
        voice_client.stop()
        message = "Skipped the current song."
        if ctx.bot.song_queue:
            next_song = ctx.bot.song_queue.pop(0)
            await play_audio(ctx, next_song)
    else:
        message = "No song is currently playing."
    await send(message)

async def leave(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel.")




async def create_embed(song_info):
    embed = Embed(title="Now Playing", description=f"{song_info['title']} by {song_info['artist']}")
    if song_info.get("album"):
        embed.set_author(name=song_info["album"])
    # Include progress bar functionality here (optional)
    return embed


# This function should be implemented in your music_utils.py file
def get_current_song_info():
    # Implement logic to retrieve information about the currently playing song
    # You can use the voice client or access specific data within your music bot logic
    pass

# Add any additional utility functions here
