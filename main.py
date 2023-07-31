import logging
import os

import discord
import docker
from discord import app_commands
from dotenv import load_dotenv

from Entities.CommandExecutor import CommandExecutor
from Entities.DockerManagerClient import DockerManagerClient
from Common.contants import APP_VERSION

# Initialize environment.
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
adminList = str(os.getenv('ADMINS'))
ADMINS = adminList.split(",")

# Set intents (permissions).
intents = discord.Intents.default()
intents.message_content = True
discordClient = DockerManagerClient(intents=intents)

# Initialize Docker Engine.
dockerClient = docker.from_env()

# Initialize logging.
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger.info('INFO: initializing DockerManagerBot')


def check_if_allowed(userId):
    userId = str(userId)
    if userId not in ADMINS:
        logger.info("[INFO] Container overview command called by non-admin.")
        raise Exception(f"Nuh-uh: {userId}")


@discordClient.event
async def on_ready():
    print(f"Client logged in as {discordClient.user}")
    logger.info(f"Version {APP_VERSION}")


@discordClient.tree.command()
async def help(interaction: discord.Interaction):
    """Overview of all possible commands"""

    check_if_allowed(interaction.user.id)

    logger.info("[INFO] Executing help command.")
    executor = CommandExecutor(dockerClient, interaction=interaction)
    await executor.get_help()


@discordClient.tree.command()
async def containers(interaction: discord.Interaction):
    """Overview of all containers."""
    check_if_allowed(interaction.user.id)

    logger.info("[INFO] Executing container overview command.")
    executor = CommandExecutor(dockerClient, interaction=interaction)
    await executor.get_containers()


@discordClient.tree.command()
@app_commands.rename(container_name='container-name')
@app_commands.describe(container_name='The name of the container to restart')
async def restart_container(interaction: discord.Interaction, container_name: str):
    """Overview of all containers."""
    check_if_allowed(interaction.user.id)

    executor = CommandExecutor(dockerClient, interaction=interaction)
    logger.info("[INFO] Restarting container.")
    await executor.restart_container(container_name)


@discordClient.tree.command()
@app_commands.rename(container_name='container-name')
@app_commands.describe(container_name='The name of the container to stop')
async def stop_container(interaction: discord.Interaction, container_name: str):
    """Overview of all containers."""
    check_if_allowed(interaction.user.id)

    executor = CommandExecutor(dockerClient, interaction=interaction)
    logger.info("[INFO] Stopping container.")
    await executor.stop_container(container_name)

discordClient.run(TOKEN)
