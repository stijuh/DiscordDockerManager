import logging
import os

import discord
import docker
from discord import app_commands
from dotenv import load_dotenv

from CommandExecutor import CommandExecutor
from DockerManagerClient import DockerManagerClient
from common import APP_VERSION, BOT_MENTION_ID

# Initialize environment.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN = int(os.getenv('ADMIN_ID'))

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
    if userId != ADMIN:
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


# In the case that the above slash commands are not working, here is a fallback method.
# This seems to happen with a docker compose setup running for more than 24 hours.
@discordClient.event
async def on_message(message):
    if message.author == discordClient.user or message.author.id != ADMIN:
        return

    if not message.content.startswith(BOT_MENTION_ID):
        return

    executor = CommandExecutor(dockerClient, message=message)
    command = str(message.content).replace(BOT_MENTION_ID, "").strip().split(" ")

    match command[0]:
        case "help":
            await executor.get_help()
        case "containers":
            await executor.get_containers()
        case "restart":
            await executor.restart_container(command[1])
        case "stop":
            await executor.stop_container(command[1])


discordClient.run(TOKEN)
