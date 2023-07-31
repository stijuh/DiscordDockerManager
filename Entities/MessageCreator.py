import json

import discord

from Common.contants import APP_VERSION


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

    async def sendSimpleMessage(self, text):
        if self.message is not None:
            await self.message.channel.send(text)
        elif self.interaction is not None:
            await self.interaction.response.send_message(text, ephemeral=True)

    async def sendEmbedWithNameAndObjectInfo(self, title, items, description="", inline=True):
        """
        Expects a list of objects in the form of {"name": "name-here", info: {object info}}.
        """

        listEmbed = get_standard_embed()
        listEmbed.title = title
        listEmbed.description = description

        for item in items:
            jsonString = json.dumps(item["info"], indent=1)
            formatted = jsonString.lstrip('{').rstrip('}')

            listEmbed.add_field(name=item["name"], value=f'```json\n{formatted}\n```', inline=inline)

        if self.message is not None:
            await self.message.channel.send(embed=listEmbed)
        else:
            await self.interaction.response.send_message(embed=listEmbed, ephemeral=True)


def get_standard_embed():
    return discord.Embed(title="Docker Manager", description="", colour=discord.Colour.blue()) \
        .set_author(name="Website: Studio Stoy", url="https://www.studiostoy.nl") \
        .set_footer(text=f"Version {APP_VERSION}")
