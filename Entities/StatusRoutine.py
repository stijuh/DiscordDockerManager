import discord
import docker
import asyncio

from Entities.CommandExecutor import CommandExecutor


# Updates every 10 seconds
async def StatusRoutine(discordClient: discord.Client, dockerClient: docker.DockerClient):
    while True:
        executor = CommandExecutor(dockerClient)
        running, total = await executor.get_running_total_containers()

        await discordClient.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{running} of {total} containers running")
        )

        await asyncio.sleep(25.0)
