#!/usr/bin/env python3

import discord
from discord import app_commands


class DockerManagerClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, guild_ids: list[str]):
        super().__init__(intents=intents)
        # Note: When using commands.Bot instead of discord.Client, the bot will maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)
        self.guild_ids = guild_ids

    # Instead of specifying a guild to every command, we copy over our global commands to the specified guilds instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild(s).
        for guild_id in self.guild_ids:
            self.tree.copy_global_to(guild=discord.Object(id=guild_id))
            await self.tree.sync(guild=discord.Object(guild_id))
