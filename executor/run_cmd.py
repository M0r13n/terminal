"""
Methods for creating docker containers that execute commands and output validation.

Note:
    You may be wondering why I decided to pass JSON between the CommandExecutor and the Docker container.
    This is needed, because the output alone is not enough to check if an challenge was solved correctly.
    Some challenges may change files, create files or delete files/folders.
    This is easy to check from inside the running container, but hard to check from outside.
"""
import json
import logging
import os
import typing
from functools import lru_cache
from json.decoder import JSONDecodeError

import docker
from docker import DockerClient

from executor.decorators import log_command
from executor.docker_config import DockerConfig
from executor.timeout import ContainerTimeout

logger = logging.getLogger(__name__)


class CommandExecutor(object):
    """
    Wrapper class around the docker API to enable cached command execution
    """

    def __init__(self, config: DockerConfig = None):
        self.config: DockerConfig = config or DockerConfig()
        self.execution_timeout: int = int(self.config.EXECUTION_TIMEOUT)
        self.docker_image: str = self.config.DOCKER_IMAGE
        self.client: DockerClient = DockerClient()
        self.init_client()

    def init_client(self):
        if self.config.DOCKER_BASE_URL is None:
            self.client = docker.from_env()
        else:
            self.client = self.make_docker_client()

    def make_docker_client(self):
        client = docker.DockerClient(
            base_url=self.config.DOCKER_BASE_URL
        )
        return client

    @property
    def images(self) -> typing.List:
        return self.client.images.list()

    @property
    def containers(self) -> typing.List:
        return self.client.containers.list()

    def get_challenge_directory_from_challenge_name(self, challenge_name) -> str:
        return os.path.join(self.config.WORKING_DIR, challenge_name)

    def prepend_python_runner_path(self, command: typing.Tuple) -> typing.Tuple:
        docker_cmd = (self.config.COMMAND_RUNNER_PATH,) + command
        return docker_cmd

    def run_command(self, command: typing.Tuple[str], challenge: str) -> bytes:
        docker_cmd = (challenge,) + command
        docker_cmd = self.prepend_python_runner_path(docker_cmd)
        docker_output = self.execute_command(tuple(docker_cmd), challenge)
        return docker_output

    def run_command_parsed(self, command: typing.Tuple[str], challenge: str) -> typing.Optional[dict]:
        docker_output = self.run_command(command, challenge)
        try:
            return json.loads(docker_output)
        except JSONDecodeError:
            logger.error("Docker response could not be JSON parsed. It was: ", docker_output)
            return None

    @log_command
    @lru_cache(maxsize=2048)
    def execute_command(self, command: typing.Tuple[str], challenge_name: str, custom_timeout: int = None) -> typing.Optional[bytes]:
        timeout = custom_timeout or self.execution_timeout
        challenge_dir = self.get_challenge_directory_from_challenge_name(challenge_name)
        with ContainerTimeout(timeout=timeout) as context:
            container = self.client.containers.run(self.docker_image, command, **self.config.runner_arguments(), working_dir=challenge_dir)
            context.container = container

        return context.container_output
