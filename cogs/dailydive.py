import random
import re

from discord import ForumChannel, Thread, RawReactionActionEvent, Guild, Embed, Interaction
from discord.app_commands import command as app_command
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

import config
from handlers import database, embedding, paginator
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

    @command(name="leaderboard", aliases=["top", "streaks", "dd"])
    async def dailydive_leaderboard(self, ctx: Context):
        entries = await self.generate_leaderboard(ctx)
        if len(entries) <= 1:
            await ctx.send(embeds=entries)
        else:
            msg = paginator.Paginator(ctx, entries)
            await msg.paginate()

    @app_command(name="leaderboard", description="View the leaderboard for daily dives")
    async def dailydive_leaderboard_ac(self, ctx: Interaction):
        entries = await self.generate_leaderboard(ctx)
        if len(entries) <= 1:
            await ctx.response.send_message(embeds=entries, ephemeral=True)
        else:
            msg = paginator.Paginator(ctx, entries, ephemeral=True)
            await msg.paginate()

    @command(name="setextrapts", aliases=["setpoints"])
    async def dailydive_set_extra_pts(self, ctx: Context, user_id: str, points: int):
        if not ctx.author.id in [config.madi_id, database.get_config_value('dailydive_operator', 0)]:
            return
        user_id = re.sub('[^0-9]','', user_id)
        if not 'extra_points' in self.thread_data:
            self.thread_data['extra_points'] = {}
        self.thread_data['extra_points'][user_id] = points
        self.sync_leaderboard_with_thread_data()
        await ctx.message.add_reaction("✅")

    @command(name="addextrapts", aliases=["addpts", "add"])
    async def dailydive_add_extra_pts(self, ctx: Context, user_id: str, points: int):
        if not ctx.author.id in [config.madi_id, database.get_config_value('dailydive_operator', 0)]:
            return
        user_id = re.sub('[^0-9]','', user_id)
        if not 'extra_points' in self.thread_data:
            self.thread_data['extra_points'] = {}
        if user_id not in self.thread_data['extra_points']:
            self.thread_data['extra_points'][user_id] = points
        else:
            self.thread_data['extra_points'][user_id] += points
        self.sync_leaderboard_with_thread_data()
        await ctx.message.add_reaction("✅")

    @command(name="subtractextrapts", aliases=["minuspts", "subtractpts", "minus", "subtract", "removepts", "rm"])
    async def dailydive_subtract_extra_pts(self, ctx: Context, user_id: str, points: int):
        if not ctx.author.id in [config.madi_id, database.get_config_value('dailydive_operator', 0)]:
            return
        user_id = re.sub('[^0-9]','', user_id)
        if not 'extra_points' in self.thread_data:
            self.thread_data['extra_points'] = {}
        if user_id not in self.thread_data['extra_points']:
            self.thread_data['extra_points'][user_id] = -points
        else:
            self.thread_data['extra_points'][user_id] -= points
        self.sync_leaderboard_with_thread_data()
        await ctx.message.add_reaction("✅")

    @command(name="resetthreaddata")
    async def dailydive_reset_thread_data(self, ctx: Context):
        if not ctx.author.id in [config.madi_id]:
            return
        self.thread_data = {}
        self.sync_leaderboard_with_thread_data()
        await ctx.message.add_reaction("✅")

    def get_current_thread(self) -> Thread:
        threads = self.dailydive_channel.threads
        threads.sort(key=(lambda t: t.created_at.timestamp()))
        return threads[-1]

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

    async def generate_leaderboard(self, ctx: Context) -> list[Embed]:
        self.load_from_db()
        self.sync_leaderboard_with_thread_data()
        value_list = []
        users = list(self.leaderboard_data.keys())
        random.shuffle(users)
        users.sort(key=lambda u: int(self.leaderboard_data[u]), reverse=True)
        placement = 0
        prev_score = 999999
        for user in users:
            score = self.leaderboard_data[user]
            emote = "✅" if user in self.thread_data[str(self.get_current_thread().id)] else "✏️"
            if score <= 0:
                continue
            if score != prev_score:
                placement += 1
            prev_score = score
            value_list.append(f"- **#{placement}・{emote}・<@{user}>・🫧 {score}**")
        return await embedding.create_info_list_embed(
            ctx,
            "",
            "## 🫧  Daily Dive Leaderboard",
            "",
            value_list,
            False,
            "If you're seeing this, please ask Madi about it.",
            False,
            max_values_per_page=10,
        )

async def setup(client):
    await client.add_cog(DailyDive(client), guilds=client.guilds)