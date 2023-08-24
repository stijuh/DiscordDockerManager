import logging
import os
import shutil
from datetime import datetime
from stat import S_IWUSR, S_IREAD

import discord
import docker
import git
import python_on_whales
from docker.models.containers import Container
from python_on_whales import DockerClient

from Entities.MessageCreator import MessageCreator

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')


class RunnerManager:
    def __init__(self, docker_sdk_client: docker.DockerClient, message_creator: MessageCreator):
        self.docker_sdk = docker_sdk_client
        self.message_creator = message_creator

    async def run_container_from_cli(self, image_name: str, cli_commands: str = None, container_name: str = None) \
            -> Container:
        return self.docker_sdk.containers.run(
            image=image_name,
            command=cli_commands,
            name=container_name,
            detach=True
        )

    async def run_container_from_git(self, git_repo_url: str, compose_name: str = "docker-compose.yml"):
        repo_name = git_repo_url.split("/")[-1].replace(".git", "")

        # Generate a timestamp-based name for the temporary folder.
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_folder_name = f"temp_{timestamp}"
        repo_path = os.path.abspath(f"temp/{temp_folder_name}/{repo_name}")

        # Clone the Git repository inside the temporary folder.
        await self.message_creator.send_simple_message(f"Pulling from repository: '**{repo_name}**'..")

        try:
            git.Repo.clone_from(url=git_repo_url, to_path=repo_path, multi_options=["--depth=1"])
            logger.info(f"[INFO] Cloned into path `{repo_path}`")

            await self.message_creator.send_simple_message(f"Pulling from repository: '**{repo_name}**'.. [SUCCESS]\n"
                                                           f"Executing `docker compose up`..", edit=True)
        except git.exc.GitCommandError as e:
            await self.message_creator.send_simple_message(f"Pulling from repository: '**{repo_name}**'.. [Error]",
                                                           edit=True)

            await self.message_creator\
                .send_exception(exception_message="Make sure the repository exists, that you have access to it and "
                                                  "that the link you provided is correct.",
                                description=f"Could not pull from repository `{repo_name}`.",
                                followup=True)
            return

        docker_whales = DockerClient(compose_files=[f"{repo_path}\\{compose_name}"])

        try:
            logger.info("[INFO] Compose up..")
            docker_whales.compose.up(detach=True)

            await self.message_creator.send_simple_message(f"Pulling from repository: '**{repo_name}**'.. [SUCCESS]\n"
                                                           f"Executing `docker compose up`.. [SUCCESS]", edit=True)
        except python_on_whales.exceptions.DockerException as e:
            logger.error("[ERROR]")
            await self.message_creator.send_simple_message(f"Pulling from repository: '**{repo_name}**'.. [SUCCESS]\n"
                                                           f"Executing `docker compose up`.. [ERROR]", edit=True)
            await self.message_creator\
                .send_exception(exception_message="Make sure the configuration is correct.\n\n"
                                                  "If environment variables are needed "
                                                  "(through .env files or other means), "
                                                  "this bot can sadly not be used to deploy it because of discord's "
                                                  "security practises. \n\nAfter manually deploying the container, "
                                                  "it can be managed through this bot.",
                                description="Could not execute `docker compose up`.",
                                followup=True)
        finally:
            logger.info("[INFO] Cleaning up temp folder.")
            self.__change_folder_attributes(repo_path)
            shutil.rmtree(f"temp")

    def __change_folder_attributes(self, folder_path):
        try:
            # Change the folder attributes to read-write for the specific git files (windows specific).
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if not file_path.endswith(".idx") and not file_path.endswith(".pack"):
                        continue

                    os.chmod(file_path, S_IREAD | S_IWUSR)  # read | write
        except Exception as e:
            print("Error:", e)
