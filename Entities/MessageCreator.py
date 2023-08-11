import discord

from Common.contants import APP_VERSION
from Entities.Paginator import Paginator


class MessageCreator:
    def __init__(self, message: discord.Message = None, interaction: discord.Interaction = None):
        self.message = None
        self.interaction = None

        if interaction is None:
            self.message = message
        elif message is None:
            self.interaction = interaction
        else:
            raise Exception("please provide either a message or an interaction.")

        self.paginator = Paginator(interaction=self.interaction)

    async def send_simple_message(self, text, file: discord.File = None, followup=False, user_only=True):
        if followup:
            await self.interaction.followup.send(text, ephemeral=user_only)
        if self.message is not None:
            await self.message.channel.send(text, file=file)
        elif self.interaction is not None:
            if file is not None:
                await self.interaction.response.send_message(text, file=file, ephemeral=user_only)
            else:
                await self.interaction.response.send_message(text, ephemeral=user_only)

    async def send_simple_embed(self, title, name: str, text: str):
        embedded = get_standard_embed()
        embedded.add_field(name=name, value=text, inline=False)

        if self.message is not None:
            await self.message.channel.send(embed=embedded)
        elif self.interaction is not None:
            await self.interaction.response.send_message(embed=embedded, ephemeral=True)

    async def send_embed_with_object_info(self, title, items, description="", items_per_page: int = 4, inline=False):
        """
        Expects a list of objects in the form of {"Name": "Object name", Info: {object info}}.
        """

        await self.paginator.send_paginated_object_info(
            title=title,
            description=description,
            items=items,
            items_per_page=items_per_page,
            inline=inline
        )


def get_standard_embed():
    return discord.Embed(title="Docker Manager", description="", colour=discord.Colour.blue()) \
        .set_author(name="Website: Studio Stoy", url="https://www.studiostoy.nl") \
        .set_footer(text=f"Version {APP_VERSION}")
