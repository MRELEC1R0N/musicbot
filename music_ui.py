# music_ui.py

from discord import ButtonStyle, InteractionType
from discord.ui import Button, View
from discord import Interaction
from discord import Message
from discord.errors import InteractionResponded

class SkipButton(Button):
    def __init__(self, cog):
        super().__init__(style=ButtonStyle.primary, label="Skip")
        self.cog = cog

    async def callback(self, interaction: Interaction):
        try:
            await interaction.response.send_message("Processing skip request...", ephemeral=True)
            await self.cog.skip_song(interaction)
        except InteractionResponded:
            pass  # interaction has already been responded to, do nothing

    async def skip_song(self, interaction):
        # Perform any necessary setup here

        try:
            # Try to send a follow-up message
            await interaction.followup.send("Skipping song...")
        except InteractionResponded:
            # The interaction has already been responded to
            pass

        # Perform the actual song skipping here

class MusicView(View):
    def __init__(self, cog):
        super().__init__()
        self.add_item(SkipButton(cog))

class PauseButton(Button):
    def __init__(self, cog):
        super().__init__(style=ButtonStyle.primary, label="Pause")
        self.cog = cog

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message("Processing pause request...", ephemeral=True)
        await self.pause_song(interaction)

    async def pause_song(self, interaction):
        # Perform any necessary setup here

        try:
            # Try to send a follow-up message
            await interaction.followup.send("Pausing song...")
        except InteractionResponded:
            # The interaction has already been responded to
            pass

        # Perform the actual song pausing here
        await self.cog.pause_song(interaction)

class ResumeButton(Button):
    def __init__(self, cog):
        super().__init__(style=ButtonStyle.primary, label="Resume")
        self.cog = cog

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message("Processing resume request...", ephemeral=True)
        await self.resume_song(interaction)

    async def resume_song(self, interaction):
        # Perform any necessary setup here

        try:
            # Try to send a follow-up message
            await interaction.followup.send("Resuming song...")
        except InteractionResponded:
            # The interaction has already been responded to
            pass

        # Perform the actual song resuming here
        await self.cog.resume_song(interaction)

class NowPlayingView(View):
    def __init__(self, cog, song_info):
        super().__init__()
        self.song_info = song_info
        self.add_item(PauseButton(cog))
        self.add_item(ResumeButton(cog))

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user == self.message.author