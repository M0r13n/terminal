import logging
import os

logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
volume_dir = os.path.join(basedir, "docker_image/ro_volume").replace('/mnt', '')

logger.debug(volume_dir)


class DockerConfig(object):
    # You are most likely not going to change these
    MEM_LIMIT = "50mb"
    NETWORK_MODE = None
    NETWORK_DISABLED = True
    REMOVE = False
    STDERR = True
    DETACH = True

    WORKING_DIR = "/challenges/"
    RO_VOLUME = "/ro_volume"
    COMMAND_RUNNER_PATH = RO_VOLUME + "/run_cmd"

    # The variables below are going to change depending on your setup
    EXECUTION_TIMEOUT = os.getenv("EXECUTION_TIMEOUT", 5)
    DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "terminal_image")
    DOCKER_BASE_URL = os.getenv("DOCKER_BASE_URL")

    @classmethod
    def runner_arguments(cls) -> dict:
        return {
            'mem_limit': cls.MEM_LIMIT,
            'network_mode': cls.NETWORK_MODE,
            'network_disabled': cls.NETWORK_DISABLED,
            'volumes': {volume_dir: {"bind": cls.RO_VOLUME, "mode": "ro"}},
            'remove': cls.REMOVE,
            'stderr': cls.STDERR,
            'detach': cls.DETACH,
        }
