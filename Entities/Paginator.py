import json
import math
import discord
from discord.ui import View, Button
from Common.contants import APP_VERSION

page_title_separation = " | page "


class Paginator:
    """Only works with interactions."""
    def __init__(self, interaction: discord.Interaction):
        self.interaction: discord.Interaction = interaction
        self.pages = []
        self.currentPage = 0

    async def send_paginated_object_info(self, title, items, description="", items_per_page: int = 4, inline=False):
        page = get_standard_embed()
        page.title = title + page_title_separation + "1"
        page.description = description

        for index, item in enumerate(items, 0):
            page: discord.Embed

            jsonString = json.dumps(item["Info"], indent=1)
            formatted = jsonString.lstrip('{').rstrip('}')

            page.add_field(name=item["Name"], value=f'```json\n{formatted}\n```', inline=inline)

            if index > 0 and (index+1) % items_per_page == 0:
                self.pages.append(page)
                page = get_standard_embed()
                page.title = title + page_title_separation + str(math.ceil(index / items_per_page) + 1)
                page.description = description

        # If there are no pages, or a not-full page left, add it.
        if len(self.pages) == 0 or len(items) % items_per_page != 0:
            self.pages.append(page)

        await self.interaction.response.send_message(embed=self.pages[self.currentPage],
                                                     view=self.getView(self.currentPage),
                                                     ephemeral=True)

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
