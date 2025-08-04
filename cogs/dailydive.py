from discord import Message, ForumChannel
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

import config
from main import Fooberry


class DailyDive(Cog, name="DailyDive"):
    def __init__(self, bot):
        self.bot: Fooberry = bot
        self.dailydive_channel: ForumChannel | None = None

    @Cog.listener()
    async def on_ready(self):
        self.dailydive_channel = self.bot.get_channel(config.dailydive_channel_id)

    @Cog.listener()
    async def on_message(self, message: Message):
        pass

    @command(name="leaderboard", aliases=["top", "streaks", "dd"])
    async def dailydive_leaderboard(self, ctx: Context):
        print(self.dailydive_channel.threads)

async def setup(client):
    await client.add_cog(DailyDive(client), guilds=client.guilds)