import logging
import os
import shutil
import sys
from datetime import datetime
from stat import S_IWUSR, S_IREAD

import docker
import git
from docker.models.containers import Container
from python_on_whales import DockerClient

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')


class RunnerManager:
    def __init__(self, docker_sdk_client: docker.DockerClient):
        self.docker_sdk = docker_sdk_client

    async def run_container_from_cli(self, image_name: str, cli_commands: str = None, container_name: str = None) \
            -> Container:
        return self.docker_sdk.containers.run(
            image=image_name,
            command=cli_commands,
            name=container_name,
            detach=True
        )

    async def run_container_from_git(self, git_repo_url: str, docker_compose_name: str = "docker-compose.yml"):
        # Create a Docker volume for temporary storage
        repo_name = git_repo_url.split("/")[-1].replace(".git", "")

        # Generate a timestamp-based name for the temporary folder
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_folder_name = f"temp_{timestamp}"
        repo_path = os.path.abspath(f"temp/{temp_folder_name}/{repo_name}")

        # Clone the Git repository inside the timestamped temporary folder
        yup = git.Repo.clone_from(url=git_repo_url, to_path=repo_path, multi_options=["--depth=1"])
        logger.info(f"[INFO] Cloned into path `{repo_path}`")

        docker_whales = DockerClient(compose_files=[f"{repo_path}\\{docker_compose_name}"])

        logger.info("[INFO] building..")
        docker_whales.compose.build()
        logger.info("[INFO] Compose up..")
        docker_whales.compose.up(detach=True)

        logger.info("Cleaning up temp folder..")
        change_folder_attributes(repo_path)

        shutil.rmtree(f"temp/{temp_folder_name}")


def change_folder_attributes(folder_path):
    try:
        # if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        #     if folder_path.startswith('.'):  # Linux and macOS
        #         os.rename(folder_path, folder_path[1:])  # Rename the folder to unhide it
        # elif os.name == 'nt':  # Windows
        #     os.system('attrib -h ' + folder_path)  # Remove the hidden attribute on Windows
        # else:
        #     print("Unsupported operating system.")

        # Change the folder attributes to read-write for all files and folders within it
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                if not file_path.endswith(".idx") and not file_path.endswith(".pack"):
                    continue

                os.chmod(file_path, S_IWUSR | S_IREAD)  # This makes the file read/write for the owner
    except Exception as e:
        print("Error:", e)
