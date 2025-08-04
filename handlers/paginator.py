from discord import Interaction
from discord.ui import button

from handlers.component_globals import ComponentBase, TIMEOUT


class PaginatorButtons(ComponentBase):
    def __init__(self, paginator, timeout):
        super().__init__(timeout=timeout)
        self.paginator = paginator

    @button(label="Previous Page")
    async def previous_page_button(self, interaction: Interaction, _: button):
        if not self.paginator.check(interaction):
            return await interaction.response.send_message("Error: There was an error performing this action. Please contact <@>.", ephemeral=True)
        await interaction.response.defer()
        return await self.paginator.backward(interaction)

    @button(label="Next Page")
    async def next_page_button(self, interaction: Interaction, _: button):
        if not self.paginator.check(interaction):
            return await interaction.response.send_message("Error: There was an error performing this action. Please contact the Bot Team.", ephemeral=True)
        await interaction.response.defer()
        return await self.paginator.forward(interaction)


class Paginator:
    def __init__(self, ctx, entries: list, pages=True):
        self.ctx = ctx
        self.entries = entries
        self.max_pages = len(entries) - 1
        self.msg = ctx.message
        self.paginating = True
        self.channel = ctx.channel
        self.current = 0
        self.pages = pages

    async def setup(self, paginator_buttons):
        if self.pages:
            self.entries[0].set_footer(text=self.footer(page=1))
        self.msg = await self.channel.send(embed=self.entries[0], view=paginator_buttons if self.max_pages != 0 else None)

    async def alter(self, page: int, interaction: Interaction):
        if self.pages:
            self.entries[page].set_footer(text=self.footer(page=page+1))
        await interaction.message.edit(embed=self.entries[page])

    async def backward(self, interaction):
        self.current = self.max_pages if self.current == 0 else self.current - 1
        await self.alter(self.current, interaction)

    async def forward(self, interaction):
        self.current = 0 if self.current == self.max_pages else self.current + 1
        await self.alter(self.current, interaction)

    def footer(self, page: int):
        return f"Page {page} of {self.max_pages + 1}"

    def check(self, interaction):
        if interaction.message.id != self.msg.id:
            return False
        return True

    async def paginate(self):
        paginator_buttons = PaginatorButtons(self, TIMEOUT)
        await self.setup(paginator_buttons)

        await paginator_buttons.wait()  # Disable the buttons after timeout
        await paginator_buttons.disable_buttons(self.msg)
