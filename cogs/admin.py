from discord.ext import commands
from discord.ext.commands import Context

import config
from config.live_config import lc
from handlers import database, embedding
from main import Fooberry


class Admin(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.bot: Fooberry = bot

    @commands.command(name="viewconfig", aliases=["vc"])
    async def view_all_config(self, ctx: Context):
        if ctx.author.id != config.madi_id:
            return
        key_list = [item for item in lc.__slots__ if type(getattr(lc, item)) in [str, int, bool, float]]
        text_list = []
        for key in key_list:
            text_list.append(f"{key}: {getattr(lc, key)}")
            if description := database.get_config_description(key):
                text_list[-1] += f"  # {description}"
        await embedding.create_info_list_embed(
            ctx=ctx,
            title="Config List",
            description=f"{len(key_list)} total config values",
            field_name="The current config values are:",
            value_list=text_list,
            send_after=True,
            error_msg="Couldn't find any config entries in the db!"
        )

    @commands.command(name="setconfigvalue", aliases=["scv"])
    async def set_config_value(self, ctx, key: str, new_value: str):
        if ctx.author.id != config.madi_id:
            return
        if config.scv_blocked.get(key):
            return await ctx.send(f"This is a blocked key! Use `{config.scv_blocked[key]}` instead.", reference=ctx.message)
        if key not in lc.__slots__:
            await ctx.message.add_reaction("❌")
            return await ctx.send(
                f"The specified key is not in the list of config entries that can be changed using this command, sorry!",
                reference=ctx.message
            )
        attr = getattr(lc, key)
        try:
            if isinstance(attr, int):
                new_value = int(new_value)
            elif isinstance(attr, float):
                new_value = float(new_value)
            elif isinstance(attr, bool):
                new_value = new_value in ['true', 'True', 't', 'T', '1', 'yes', 'Yes', 'YES']
        except ValueError:
            await ctx.message.add_reaction("❌")
            return await ctx.send(
                f"You must specify a new value of the correct datatype.",
                reference=ctx.message
            )
        lc.set(key, new_value)
        await ctx.message.add_reaction("✅")

    @commands.command(name="setconfigdescription", aliases=["scd"])
    async def set_config_description(self, ctx, key: str, *args):
        if ctx.author.id != config.madi_id:
            return
        if not args:
            await ctx.message.add_reaction("❌")
            return await ctx.send(f"Please specify a description to be set!", reference=ctx.message)
        new_description = " ".join(args)
        key_list = [item for item in lc.__slots__ if type(getattr(lc, item)) in [str, int, bool, float]]
        if key not in key_list:
            await ctx.message.add_reaction("❌")
            return await ctx.send(
                f"The specified key is not in the list of config entries that can be changed using this command, sorry!",
                reference=ctx.message)
        database.set_config_description(key, new_description)
        await ctx.message.add_reaction("✅")

    @commands.command(name="sync")
    async def sync_commands(self, ctx, guild_id=-1):
        if ctx.author.id != config.madi_id:
            return
        if guild_id > 0:
            await self.bot.tree.sync(guild=self.bot.get_guild(guild_id))
        else:
            await self.bot.tree.sync()

async def setup(client: Fooberry):
    await client.add_cog(Admin(client), guilds=client.guilds)
