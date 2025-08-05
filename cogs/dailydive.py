import re

from discord import Message, ForumChannel, Thread, RawReactionActionEvent, Guild
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

import config
from handlers import database, embedding
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
        if event.channel_id == self.get_current_thread().id and event.message_author_id == event.user_id:
            self.add_to_thread_data(str(event.channel_id), str(event.message_author_id))

    def load_from_db(self):
        self.leaderboard_data = database.get_config_value('dailydive_leaderboard_data', {})
        self.thread_data = database.get_config_value('dailydive_thread_data', {})

    def update_to_db(self):
        database.set_config_value('dailydive_leaderboard_data', self.leaderboard_data)
        database.set_config_value('dailydive_thread_data', self.thread_data)

    def add_to_thread_data(self, ch: str, author: str):
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
                else:
                    self.add_leaderboard_points(author)
        self.update_to_db()

    def add_leaderboard_points(self, author: str, pts: int = 1):
        if author not in self.leaderboard_data:
            self.leaderboard_data[author] = pts
        else:
            self.leaderboard_data[author] += pts
        if self.leaderboard_data[author] == 0:
            self.leaderboard_data.pop(author)

    @command(name="leaderboard", aliases=["top", "streaks", "dd"])
    async def dailydive_leaderboard(self, ctx: Context):
        self.load_from_db()
        value_list = []
        for user in self.leaderboard_data:
            value_list.append(f"<@{user}>: {self.leaderboard_data[user]}")
        await embedding.create_info_list_embed(ctx, "Daily Dive Leaderboard", "Number of days each user has responded to the daily dive.\nSelf-react to get your response counted!", "", value_list, True, "If you're seeing this, please ask Madi about it.", False)

    @command(name="setextrapts", aliases=["setpoints", "points", "pts"])
    async def dailydive_set_extra_pts(self, _ctx: Context, user_id: str, points: int):
        user_id = re.sub('[^0-9]','', user_id)
        if not 'extra_points' in self.thread_data:
            self.thread_data['extra_points'] = {}
        self.thread_data['extra_points'][user_id] = points
        self.sync_leaderboard_with_thread_data()

    @command(name="resetthreaddata")
    async def dailydive_reset_thread_data(self, _ctx: Context):
        self.thread_data = {}
        self.update_to_db()

    def get_current_thread(self) -> Thread:
        threads = self.dailydive_channel.threads
        threads.sort(key=(lambda t: t.created_at.timestamp()))
        return threads[-1]

async def setup(client):
    await client.add_cog(DailyDive(client), guilds=client.guilds)