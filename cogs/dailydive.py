from pyexpat.errors import messages

from discord import Message, ForumChannel, Thread
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

import config
from config.live_config import lc
from handlers import database
from main import Fooberry


class DailyDive(Cog, name="DailyDive"):
    def __init__(self, bot):
        self.bot: Fooberry = bot
        self.dailydive_channel: ForumChannel | None = None
        self.leaderboard_data: dict = {}
        self.thread_data: dict = {}

    @Cog.listener()
    async def on_ready(self):
        self.dailydive_channel = self.bot.get_channel(config.dailydive_channel_id)
        self.load_from_db()

    def load_from_db(self):
        self.leaderboard_data = database.get_config_value('dailydive_leaderboard_data', {})
        self.thread_data = database.get_config_value('dailydive_thread_data', {})

    def update_to_db(self):
        database.set_config_value('dailydive_leaderboard_data', self.leaderboard_data)
        database.set_config_value('dailydive_thread_data', self.thread_data)

    def add_to_thread_data(self, ch: int, author: int):
        if ch in self.thread_data:
            if author not in self.thread_data[ch]:
                self.thread_data[ch].append(author)
        else:
            self.thread_data[ch] = [author]
        self.update_to_db()

    def sync_leaderboard_with_thread_data(self):
        new_leaderboard_data = {}
        for ch in self.thread_data:
            for author in self.thread_data[ch]:
                if author not in new_leaderboard_data:
                    new_leaderboard_data[author] = 1
                else:
                    new_leaderboard_data[author] += 1
        self.leaderboard_data = new_leaderboard_data
        self.update_to_db()

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.channel != self.get_current_thread() and self.message_condition(message.content):
            return
        self.load_from_db()
        self.add_to_thread_data(message.channel.id, message.author.id)

    @command(name="leaderboard", aliases=["top", "streaks", "dd"])
    async def dailydive_leaderboard(self, ctx: Context):
        await ctx.send(str(self.thread_data))

    def message_condition(self, _message: str) -> bool:
        return True

    def get_current_thread(self) -> Thread:
        threads = self.dailydive_channel.threads
        threads.sort(key=(lambda t: t.created_at.timestamp()))
        return threads[-1]

async def setup(client):
    await client.add_cog(DailyDive(client), guilds=client.guilds)