from discord import Embed, Interaction
from discord.app_commands import command as app_command
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands.context import Context

from handlers import embedding, paginator
from main import Fooberry


class Help(Cog, name="Help"):
    def __init__(self, bot):
        self.bot: Fooberry = bot

    @command(name="help", aliases=["h"])
    async def help(self, ctx: Context):
        entries = await self.generate_help(ctx)
        if len(entries) <= 1:
            await ctx.send(embeds=entries, ephemeral=True)
        else:
            msg = paginator.Paginator(ctx, entries)
            await msg.paginate()

    @app_command(name="help", description="View helpful info for FooberryBot.")
    async def help_ac(self, ctx: Interaction):
        entries = await self.generate_help(ctx)
        if len(entries) <= 1:
            await ctx.response.send_message(embeds=entries, ephemeral=True)
        else:
            msg = paginator.Paginator(ctx, entries, ephemeral=True)
            await msg.paginate()

    async def generate_help(self, ctx: Context | Interaction) -> list[Embed]:
        return await embedding.create_info_list_embed(
            ctx,
            "FooberryBot Commands",
            "",
            "",
            [
                "**`!leaderboard`** / **`!dd`** / **`!top`** / **`/leaderboard`**\n"
                "View the leaderboard for <#1400699611974471754>, and check everyone's status on whether they've posted today.",
                "**`!add <userid / @user> <amount>`**\n"
                "Add daily dive points to a user (admin-only).",
                "**`!subtract <userid / @user> <amount>`** / **`!minus`** / **`!rm`**\n"
                "Revoke daily dive points from a user (admin-only).",
            ],
            send_after=False,
            code_blocks=False,
        )

async def setup(client):
    await client.add_cog(Help(client), guilds=client.guilds)