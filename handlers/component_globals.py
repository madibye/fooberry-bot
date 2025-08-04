from dataclasses import dataclass
from typing import List

from discord import Interaction, Message, TextStyle
from discord.ext.commands import Context
from discord.ui import View, Button, Select, Modal, TextInput


@dataclass
class TextInputInfo:
    label: str
    placeholder: str
    style: TextStyle
    max_length: int
    required: bool
    custom_id: str


class ModalComponentData:
    def __init__(self, interaction: Interaction):
        self.value: List[str] = [data['components'][0]['value'] for data in interaction.data['components']]
        self.type: List[int] = [int(data['components'][0]['type']) for data in interaction.data['components']]
        self.custom_id: List[str] = [data['components'][0]['custom_id'] for data in interaction.data['components']]


class ComponentBase(View):
    """
    Dedicated for button component classes to inherit
    Contains useful methods that are generally used when dealing with components
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def check_author(interaction: Interaction, ctx: Context):
        return interaction.user == ctx.author

    async def disable_buttons(self, message: Message):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        await message.edit(view=self)

    async def disable_selects(self, message: Message):
        for item in self.children:
            if isinstance(item, Select):
                item.disabled = True

        await message.edit(view=self)

    def add_link_button(self, label, url, emoji=None):
        self.add_item(Button(label=label, url=url, emoji=emoji))


class ModularModal(Modal):
    interaction = None

    def __init__(self, timeout, title, inputs):
        super().__init__(timeout=timeout, title=title)

        for text_input in inputs:
            self.add_item(TextInput(
                label=text_input.label,
                style=text_input.style,
                placeholder=text_input.placeholder,
                max_length=text_input.max_length,
                required=text_input.required,
                custom_id=text_input.custom_id,
            ))

    async def on_submit(self, interaction):
        self.interaction = interaction
        self.stop()


# Useful values
TIMEOUT = 180
