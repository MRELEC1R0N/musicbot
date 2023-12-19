# music_ui.py

from discord import ButtonStyle, InteractionType
from discord.ui import Button, View
from discord import Interaction
from discord import Message

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

class NowPlayingView(View):
    def __init__(self, song_info):
        super().__init__()
        self.song_info = song_info

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user == self.message.author