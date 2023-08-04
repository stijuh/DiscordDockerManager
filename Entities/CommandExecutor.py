import os

import discord
import docker
import requests
from docker.models.containers import Container

from Common.methods import parseAndGetFormattedTimeDifference, strip_ansi_escape_codes
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
                "Name": "General",
                "Info": {
                    "Info": "When using commands where you provide a container name and the exact container is "
                            "not found, there might be suggestions for related containers.",
                    "Example": "Actual name: 'todo-app-db', you provide: 'todo'. "
                               "-> a list of related containers with the correct name is sent."
                }
            },
            {
                "Name": "Help",
                "Info": {
                    "Command:": "/help",
                    "Description": "I think you know what this does by now."
                }
            },
            {
                "Name": "Get all containers",
                "Info": {
                    "Command:": "/containers"
            }
            },
            {
                "Name": "Restart container",
                "Info": {
                    "Command:": "/restart_container"
                }
            },
            {
                "Name": "Stop container",
                "Info": {
                    "Command:": "/stop_container"
                }
            },
            {
                "Name": "Rename a container",
                "Info": {
                    "Command:": "/rename_container"
                }
            },
            {
                "Name": "Get logs of a container",
                "Info": {
                    "Command:": "/rename_container",
                    "Description": "Retrieves the recent logs from a container as a txt file."
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
        await self.__raise_if_manager(container_name)

        try:
            containerInfo: Container = self.dockerClient.containers.get(container_name)
            await self.messageCreator.sendSimpleMessage(f"Restarting container: `{container_name}`")
            containerInfo.restart()
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(container_name)

    async def stop_container(self, container_name: str):
        await self.__raise_if_manager(container_name)

        try:
            containerInfo: Container = self.dockerClient.containers.get(container_name)
            await self.messageCreator.sendSimpleMessage(f"Stopping container: `{container_name}`")
            containerInfo.stop()
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(container_name)

    async def rename_container(self, old_container_name: str, new_container_name):
        try:
            containerInfo: Container = self.dockerClient.containers.get(old_container_name)
            await self.messageCreator.sendSimpleMessage(f"Renaming container: `{old_container_name}` "
                                                        f"to {new_container_name}")
            containerInfo.rename(new_container_name)
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(old_container_name)

    async def retrieve_logs_from_container(self, container_name):
        try:
            containerInfo: Container = self.dockerClient.containers.get(container_name)

            decoded_logs = containerInfo.logs().decode()
            logs_without_ansi = strip_ansi_escape_codes(decoded_logs)

            tempFileName = f'temp/{containerInfo.name}-logs.txt'
            with open(tempFileName, 'w') as f:
                f.write(logs_without_ansi)

            await self.messageCreator.sendSimpleMessage(f"Here are the logs of container **{containerInfo.name}**:",
                                                        file=discord.File(tempFileName))
            os.remove(tempFileName)
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(container_name)

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

    async def __send_other_possible_containers(self, container_name: str):
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

    async def __raise_if_manager(self, container_name):
        if container_name == "docker-manager-discord":
            await self.messageCreator.sendSimpleMessage("You cannot kill me, mortal")
            raise Exception("Nope, I stay online forever.")
