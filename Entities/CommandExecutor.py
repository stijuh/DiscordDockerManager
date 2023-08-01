import discord
import docker

from Common.methods import parseAndGetFormattedTimeDifference
from Entities.MessageCreator import MessageCreator
from Entities.Pagination import Pagination


class CommandExecutor:
    def __init__(self, dockerClient: docker.DockerClient, message: discord.Message = None,
                 interaction: discord.Interaction = None):
        self.dockerClient = dockerClient
        self.message = message
        self.interaction = interaction

        self.messageCreator = MessageCreator(message=message, interaction=interaction)

    async def get_help(self):
        listOfCommands = [
            {
                "name": "Help",
                "info": {
                    "slash:": "/help"
                }
            },
            {
                "name": "Get all containers",
                "info": {
                    "slash:": "/containers"
                }
            },
            {
                "name": "Restart container",
                "info": {
                    "slash:": "/restart_container"
                }
            },
            {
                "name": "Stop container",
                "info": {
                    "slash:": "/stop_container"
                }
            }
        ]

        await self.messageCreator.sendEmbedWithNameAndObjectInfo(
            title="Help menu",
            description="Overview of all possible commands.",
            items=listOfCommands,
            inline=False
        )

    async def get_containers(self):
        containers = self.dockerClient.containers.list(all=True)
        containerInfoList = []

        for container in containers:
            containerInfo = {
                "name": container.name,
                "info": {
                    "Status": container.status,
                    "Started": container.attrs.get("State")["StartedAt"][:10],
                    "Running for": parseAndGetFormattedTimeDifference(container.attrs.get("State")["StartedAt"])
                }
            }

            containerInfoList.append(containerInfo)

        paginator = Pagination(interaction=self.interaction)
        await paginator.send_paginated_object_info(
            title="Containers",
            description="To manage a specific container, use the container's name.",
            items=containerInfoList,
        )

    async def restart_container(self, container_name: str):
        await self.raise_if_manager(container_name)

        await self.messageCreator.sendSimpleMessage(f"Restarting container: `{container_name}`")
        containerToRestart = self.dockerClient.containers.get(container_name)
        containerToRestart.restart()

    async def stop_container(self, container_name: str):
        await self.raise_if_manager(container_name)

        await self.messageCreator.sendSimpleMessage(f"Stopping container: `{container_name}`")
        containerToRestart = self.dockerClient.containers.get(container_name)
        containerToRestart.stop()

    async def raise_if_manager(self, container_name):
        if container_name == "docker-manager-discord":
            await self.messageCreator.sendSimpleMessage("You cannot kill me, mortal")
            raise Exception("Nope, I stay online forever.")
