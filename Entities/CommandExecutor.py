import discord
import docker
import requests

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

    async def get_and_send_containers(self, filter_name: str = ""):
        containers = await self.__get_containers(filter_name)

        paginator = Pagination(interaction=self.interaction)
        await paginator.send_paginated_object_info(
            title="Containers",
            description="To manage a specific container, use the container's name.",
            items=containers,
        )

    async def restart_container(self, container_name: str):
        await self.raise_if_manager(container_name)

        try:
            containerToRestart = self.dockerClient.containers.get(container_name)
            await self.messageCreator.sendSimpleMessage(f"Restarting container: `{container_name}`")
            containerToRestart.restart()
        except requests.exceptions.HTTPError:
            await self.__send_possible_containers(container_name)

    async def stop_container(self, container_name: str):
        await self.raise_if_manager(container_name)

        try:
            containerToRestart = self.dockerClient.containers.get(container_name)
            await self.messageCreator.sendSimpleMessage(f"Stopping container: `{container_name}`")
            containerToRestart.stop()
        except requests.exceptions.HTTPError:
            await self.__send_possible_containers(container_name)

    async def raise_if_manager(self, container_name):
        if container_name == "docker-manager-discord":
            await self.messageCreator.sendSimpleMessage("You cannot kill me, mortal")
            raise Exception("Nope, I stay online forever.")

    # Private methods
    async def __get_containers(self, filter_name: str = ""):
        containers = self.dockerClient.containers.list(all=True)
        containerInfoList = []

        for container in containers:
            if filter_name not in container.name:
                continue

            containerInfo = {
                "name": container.name,
                "info": {
                    "Status": container.status,
                    "Started": container.attrs.get("State")["StartedAt"][:10],
                    "Running for": parseAndGetFormattedTimeDifference(container.attrs.get("State")["StartedAt"])
                }
            }

            containerInfoList.append(containerInfo)

        return containerInfoList

    async def __send_possible_containers(self, container_name: str):
        containers = await self.__get_containers(container_name)

        # If there are any containers that contain that name, show them.
        if len(containers) > 0:
            paginator = Pagination(interaction=self.interaction)
            await paginator.send_paginated_object_info(
                title=f"Could not find container with that name: `{container_name}`",
                description="Did you mean one of these?",
                items=containers,
            )
        else:
            await self.messageCreator.sendSimpleMessage(f"Could not find specific or related containers with name: `{container_name}`")
