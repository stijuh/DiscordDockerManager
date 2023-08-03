import logging
import os

import discord
import docker
from discord import app_commands
from docker.errors import DockerException
from dotenv import load_dotenv

from Entities.CommandExecutor import CommandExecutor
from Entities.DockerManagerClient import DockerManagerClient
from Common.contants import APP_VERSION

# Initialize logging.
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger.info('[INFO] initializing DockerManagerBot')

# Initialize environment.
logger.info('[INFO] Updating environment variables')
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
adminList = str(os.getenv('ADMINS'))
ADMINS = adminList.split(",")

# Set intents (permissions).
logger.info('[INFO] Setting discord intents (permissions)')
intents = discord.Intents.default()
intents.message_content = True
discordClient = DockerManagerClient(intents=intents)

# Initialize Docker Engine.
logger.info('[INFO] Trying to get the docker client from the environment..')
dockerClient = None
try:
    dockerClient = docker.from_env()
except DockerException:
    logger.error('[ERROR] Could not connect to docker. \nMake sure that docker is running, and this app is running '
                 'in the same environment.')
    exit("Exiting application.")


def check_if_allowed(userId):
    userId = str(userId)
    if userId not in ADMINS:
        logger.warning("[INFO] Container overview command called by non-admin.")
        raise Exception(f"Nuh-uh: user {userId} is not a registereds admin.")


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
@app_commands.rename(container_filter='container-name')
@app_commands.describe(container_filter='Leave empty to get all containers')
async def containers(interaction: discord.Interaction, container_filter: str = ""):
    """Overview of all containers. Use the filter to look for specific containers"""
    check_if_allowed(interaction.user.id)

    logger.info("[INFO] Executing container overview command.")
    executor = CommandExecutor(dockerClient, interaction=interaction)
    await executor.get_and_send_containers(container_filter)


@discordClient.tree.command()
@app_commands.rename(container_name='container-name')
@app_commands.describe(container_name='The name of the container to restart, or to search for containers')
async def restart_container(interaction: discord.Interaction, container_name: str):
    """Overview of all containers."""
    check_if_allowed(interaction.user.id)

    executor = CommandExecutor(dockerClient, interaction=interaction)
    logger.info("[INFO] Executing restart container command.")
    await executor.restart_container(container_name)


@discordClient.tree.command()
@app_commands.rename(container_name='container-name')
@app_commands.describe(container_name='The name of the container to stop')
async def stop_container(interaction: discord.Interaction, container_name: str):
    """Overview of all containers."""
    check_if_allowed(interaction.user.id)

    executor = CommandExecutor(dockerClient, interaction=interaction)
    logger.info("[INFO] Executing stop container command.")
    await executor.stop_container(container_name)

discordClient.run(TOKEN)
