from datetime import timedelta

from discord import Colour, Embed
from discord.ext.commands import Context

from handlers.paginator import Paginator

def get_time_remaining_str(time_remaining: timedelta):
    if time_remaining.total_seconds() >= 86400:
        return f"{round(time_remaining.total_seconds() / 86400)} {'days' if time_remaining.total_seconds() >= 172800 else 'day'}"
    if time_remaining.total_seconds() >= 3600:
        return f"{round(time_remaining.total_seconds() / 3600)} {'hours' if time_remaining.total_seconds() >= 7200 else 'hour'}"
    if time_remaining.total_seconds() >= 60:
        return f"{round(time_remaining.total_seconds() / 60)} {'minutes' if time_remaining.total_seconds() >= 120 else 'minute'}"
    return f"{round(time_remaining.total_seconds())} {'seconds' if time_remaining.total_seconds() >= 2 else 'second'}"

async def create_info_list_embed(
    ctx: Context, title: str, description: str, field_name: str, value_list: list[str],
    send_after: bool = False, error_msg: str = "Sorry, there are no entries to display.", code_blocks: bool = True, colour: Colour = Colour.green(),
) -> list[Embed]:
    """
    :param ctx: Discord context object, should always be passed for the purposes of being able to send messages within the function
    :param title: Embed title (will apply to all embeds created)
    :param description: Embed description (will apply to all embeds created)
    :param field_name: Embed field name (will apply to all embeds created)
    :param value_list: The list of values that will be added to the embed field.
    The function scrolls through each item in this list and, if the embed gets too big, it'll create a new page.
    :param send_after: If True, the function will send the embeds created.
    Will create a paginator if multiple embeds are created, otherwise it'll just send the singular embed as is.
    :param error_msg: Error message that will display if len(value_list) == 0.
    :param code_blocks: Toggles whether or not the value list will be displayed in a code block.
    :param colour: Embed colour
    :return: Returns a list of embeds created
    """
    entries: list[Embed] = [Embed(title=title, description=description, colour=colour)]
    words = []
    for word in value_list:
        if len(entries[-1]) + len(' \n'.join(words)) + len(word) < 1024 and len(words) < 25:
            words.append(word)
        else:
            joined_list = " \n".join(words)
            entries[-1].add_field(name=field_name, value=f"{'```' if code_blocks else ''}{joined_list}{'```' if code_blocks else ''}")
            words = [word]
            entries.append(Embed(title=title, description=description, colour=colour))
    joined_list = " \n".join(words)
    entries[-1].add_field(name=field_name, value=f"{'```' if code_blocks else ''}{joined_list}{'```' if code_blocks else ''}")
    if send_after:
        if len(entries) > 1 and len(value_list) > 0:
            em = Paginator(ctx=ctx, entries=entries)
            await em.paginate()
        elif len(entries) == 1 and len(value_list) > 0:
            await ctx.send(embed=entries[0], reference=ctx.message)
        else:
            await ctx.send(error_msg, reference=ctx.message)
    return entries
