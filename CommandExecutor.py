import discord
import docker

from MessageCreator import MessageCreator


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
                    "slash:": "/help",
                    "text:": "help"
                }
            },
            {
                "name": "Get all containers",
                "info": {
                    "slash:": "/containers",
                    "text:": "containers"
                }
            },
            {
                "name": "Restart container",
                "info": {
                    "slash:": "/restart_container",
                    "text:": "restart <name>"
                }
            },
            {
                "name": "Stop container",
                "info": {
                    "slash:": "/stop_container",
                    "text:": "stop <name>"
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
                    "status": container.status,
                    "started": container.attrs.get("State")["StartedAt"][:10]
                }
            }

            containerInfoList.append(containerInfo)

        await self.messageCreator.sendEmbedWithNameAndObjectInfo(
            title="Containers",
            description="To manage a specific container, use the container's name.",
            items=containerInfoList,
            inline=False
        )

    async def restart_container(self, container_name: str):
        await self.raise_if_manager(container_name)

        containerToRestart = self.dockerClient.containers.get(container_name)
        containerToRestart.restart()
        await self.messageCreator.sendSimpleMessage(f"Restarting container: `{container_name}`")

    async def stop_container(self, container_name: str):
        await self.raise_if_manager(container_name)

        containerToRestart = self.dockerClient.containers.get(container_name)
        containerToRestart.stop()
        await self.messageCreator.sendSimpleMessage(f"Stopping container: `{container_name}`")

    async def raise_if_manager(self, container_name):
        if container_name == "docker-manager-discord":
            await self.messageCreator.sendSimpleMessage("Nuh-uh! You cannot kill me, mortal")
            raise Exception("Nuh-uh! i stay online forever.")
