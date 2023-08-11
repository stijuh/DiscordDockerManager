import os

import discord
import docker
import requests
from docker.errors import NotFound
from docker.models.containers import Container

from Common.contants import APP_NAME
from Common.utils import parseAndGetFormattedTimeDifference, strip_ansi_escape_codes
from Entities.MessageCreator import MessageCreator


class CommandExecutor:
    def __init__(self, dockerClient: docker.DockerClient, message: discord.Message = None,
                 interaction: discord.Interaction = None):
        self.docker_client = dockerClient
        self.message = message
        self.interaction = interaction

        self.message_creator = MessageCreator(message=message, interaction=interaction)

    async def get_running_total_containers(self) -> (int, int) :
        running = len(self.docker_client.containers.list())
        total = len(self.docker_client.containers.list(all=True))

        return running, total

    async def get_help(self):
        listOfCommands = [
            {
                "Name": "General",
                "Info": "When using commands where you provide a container name and the exact container is not found, "
                        "there might be suggestions for related containers."
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

        await self.message_creator.send_embed_with_object_info(
            title="Help menu",
            description="Overview of all possible commands.",
            items=listOfCommands,
            items_per_page=5,
        )

    async def get_and_send_containers(self, filter_name: str = ""):
        containers = await self.get_containers_formatted(filter_name)

        if len(containers) == 0 or (len(containers) == 1 and containers[0]["Name"] == APP_NAME):
            await self.message_creator.send_simple_message("There are currently no other containers found! Start one, "
                                                           "and run the command again.")
        else:
            await self.message_creator.send_embed_with_object_info(
                title="Containers",
                description="To manage a specific container, use the container's name.",
                items=containers,
            )

    async def restart_container(self, container_name: str):
        await self.__raise_if_manager(container_name)

        try:
            containerInfo: Container = self.docker_client.containers.get(container_name)
            await self.message_creator.send_simple_message(f"Restarting container: `{container_name}`")
            containerInfo.restart()
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(container_name)

    async def stop_container(self, container_name: str):
        await self.__raise_if_manager(container_name)

        try:
            containerInfo: Container = self.docker_client.containers.get(container_name)
            await self.message_creator.send_simple_message(f"Stopping container: `{container_name}`")
            containerInfo.stop()
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(container_name)

    async def rename_container(self, old_container_name: str, new_container_name):
        await self.__raise_if_manager(old_container_name)

        try:
            containerInfo: Container = self.docker_client.containers.get(old_container_name)
            await self.message_creator.send_simple_message(f"Renaming container: `{old_container_name}` "
                                                           f"to `{new_container_name}`")
            containerInfo.rename(new_container_name)
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(old_container_name)

    async def retrieve_logs_from_container(self, container_name):
        try:
            containerInfo: Container = self.docker_client.containers.get(container_name)

            decoded_logs = containerInfo.logs().decode()
            logs_without_ansi = strip_ansi_escape_codes(decoded_logs)

            tempFileName = f'temp/{containerInfo.name}-logs.txt'
            with open(tempFileName, 'w') as f:
                f.write(logs_without_ansi)

            await self.message_creator.send_simple_message(f"Here are the logs of container **{containerInfo.name}**:",
                                                           file=discord.File(tempFileName))
            os.remove(tempFileName)
        except NotFound:
            await self.__send_other_possible_containers(container_name)

    async def remove_container(self, container_name):
        await self.__raise_if_manager(container_name)

        try:
            containerInfo: Container = self.docker_client.containers.get(container_name)
            await self.message_creator.send_simple_message(f"Removing container: `{container_name}`")
            containerInfo.remove()
        except requests.exceptions.HTTPError:
            await self.__send_other_possible_containers(container_name)

    async def get_containers_formatted(self, filter_name: str = ""):
        containers = self.docker_client.containers.list(all=True)
        containerInfoList = []

        for container in containers:
            if filter_name.lower() not in container.name.lower():
                continue

            runningFor = ""
            if container.status == "running":
                runningFor = parseAndGetFormattedTimeDifference(container.attrs.get("State")["StartedAt"])

            containerInfo = {
                "Name": container.name,
                "Info": {
                    "Status": container.status,
                    "Started": container.attrs.get("State")["StartedAt"][:10],
                    "Running for": runningFor
                }
            }

            containerInfoList.append(containerInfo)

        return containerInfoList

    # Private methods
    async def __send_other_possible_containers(self, container_name: str):
        containers = await self.get_containers_formatted(container_name)

        # If there are any containers that contain that name, show them.
        if len(containers) > 0:
            await self.message_creator.send_embed_with_object_info(
                title=f"Could not find container with that name: `{container_name}`",
                description="Did you mean one of these?",
                items=containers
            )
        else:
            await self.message_creator.send_simple_message(f"Could not find specific or related containers with name: "
                                                           f"`{container_name}`")

    async def __raise_if_manager(self, container_name):
        if container_name == APP_NAME:
            await self.message_creator.send_simple_message("You cannot kill me, mortal")
            raise Exception("Nope, I stay online forever.")
