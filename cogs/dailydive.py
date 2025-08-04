from discord import Message, ForumChannel, Thread
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
        if message.channel != self.get_current_thread():
            return

    @command(name="leaderboard", aliases=["top", "streaks", "dd"])
    async def dailydive_leaderboard(self, ctx: Context):
        await ctx.send(self.get_current_thread().name)

    def get_current_thread(self) -> Thread:
        threads = self.dailydive_channel.threads
        threads.sort(key=(lambda t: t.created_at.timestamp()))
        return threads[-1]

async def setup(client):
    await client.add_cog(DailyDive(client), guilds=client.guilds)