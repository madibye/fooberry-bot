import re

from discord import Message, ForumChannel, Thread, RawReactionActionEvent, Guild
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

import config
from handlers import database
from main import Fooberry


class DailyDive(Cog, name="DailyDive"):
    def __init__(self, bot):
        self.bot: Fooberry = bot
        self.dailydive_channel: ForumChannel | None = None
        self.guild: Guild | None = None
        self.leaderboard_data: dict = {}
        self.thread_data: dict = {}

    @Cog.listener()
    async def on_ready(self):
        self.dailydive_channel = self.bot.get_channel(config.dailydive_channel_id)
        self.guild = self.dailydive_channel.guild
        self.load_from_db()

    @Cog.listener()
    async def on_raw_reaction_add(self, event: RawReactionActionEvent):
        if event.message_author_id == event.user_id:
            self.add_to_thread_data(event.channel_id, event.message_author_id)

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
        self.sync_leaderboard_with_thread_data()

    def sync_leaderboard_with_thread_data(self):
        self.leaderboard_data = {}
        for ch in self.thread_data:
            for author in self.thread_data[ch]:
                if ch == 'extra_points':
                    self.add_leaderboard_points(author, self.thread_data[ch][author])
                self.add_leaderboard_points(author)
        self.update_to_db()

    def add_leaderboard_points(self, author: int, pts: int = 1):
        if author not in self.leaderboard_data:
            self.leaderboard_data[author] = pts
        else:
            self.leaderboard_data[author] += pts

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.channel != self.get_current_thread() and self.message_condition(message.content):
            return
        self.load_from_db()
        self.add_to_thread_data(message.channel.id, message.author.id)

    @command(name="leaderboard", aliases=["top", "streaks", "dd"])
    async def dailydive_leaderboard(self, ctx: Context):
        await ctx.send(str(self.leaderboard_data))

    @command(name="setextrapts", aliases=["setpoints", "points", "pts"])
    async def dailydive_set_extra_pts(self, _ctx: Context, user_id: str, points: int):
        user_id = int(re.sub('[^0-9]','', user_id))
        self.thread_data['extra_points'][user_id] = points
        self.sync_leaderboard_with_thread_data()

    @staticmethod
    def message_condition(_message: str) -> bool:
        return True

    def get_current_thread(self) -> Thread:
        threads = self.dailydive_channel.threads
        threads.sort(key=(lambda t: t.created_at.timestamp()))
        return threads[-1]

async def setup(client):
    await client.add_cog(DailyDive(client), guilds=client.guilds)