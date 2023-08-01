import json
import math

import discord
from discord.ui import View, Button

from Common.contants import APP_VERSION


class Pagination:
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.pages = []
        self.currentPage = 0

    async def send_paginated_object_info(self, title, items, description=""):
        page = get_standard_embed()
        page.title = title
        page.description = description

        for index, item in enumerate(items, 0):
            page: discord.Embed

            if index > 0 and index % 4 == 0:
                self.pages.append(page)
                page = get_standard_embed()
                page.title = title + f" | page {math.ceil(index / 4)}"
                page.description = description

            jsonString = json.dumps(item["info"], indent=1)
            formatted = jsonString.lstrip('{').rstrip('}')

            page.add_field(name=item["name"], value=f'```json\n{formatted}\n```', inline=False)

        # If there's a not fully page left, add it too
        if len(items) % 4 != 0:
            self.pages.append(page)

        await self.interaction.response.send_message(embed=self.pages[self.currentPage], view=self.getView(self.currentPage), ephemeral=True)

    def getView(self, pagePosition):
        buttons = [
            Button(emoji="⏮️", label=' ', style=discord.ButtonStyle.blurple, custom_id='nav_first'),
            Button(emoji="⬅️", label=' ', style=discord.ButtonStyle.blurple, custom_id='nav_back'),
            Button(emoji="➡️", label=' ', style=discord.ButtonStyle.blurple, custom_id='nav_next'),
            Button(emoji="⏭️", label=' ', style=discord.ButtonStyle.blurple, custom_id='nav_last')
        ]
        view = View(timeout=None)

        # set navigation callback to buttons and add them to the view
        for button in buttons:
            if button.custom_id == "nav_first" or button.custom_id == "nav_back":
                button.disabled = pagePosition <= 0
            elif button.custom_id == "nav_last" or button.custom_id == "nav_next":
                button.disabled = pagePosition >= len(self.pages) - 1

            button.callback = self.page_navigation
            view.add_item(button)

        return view

    async def page_navigation(self, interaction: discord.Interaction):
        match interaction.data["custom_id"]:
            case "nav_first":
                self.currentPage = 0
            case "nav_next":
                self.currentPage += 1
            case "nav_back":
                self.currentPage -= 1
            case "nav_last":
                self.currentPage = len(self.pages) - 1

        await interaction.response.edit_message(embed=self.pages[self.currentPage], view=self.getView(self.currentPage))


def get_standard_embed():
    return discord.Embed(title="Docker Manager", description="", colour=discord.Colour.blue()) \
        .set_author(name="Website: Studio Stoy", url="https://www.studiostoy.nl") \
        .set_footer(text=f"Version {APP_VERSION}")
