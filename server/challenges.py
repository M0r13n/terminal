import logging
import os
from functools import lru_cache

from server.cache import cache_command
from server.decorators import log_cache_status
from server.extensions import c
from server.parse import split_command

logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
challenge_dir = os.path.join(basedir, "../executor/docker_image/ro_volume")
challenge_file = os.path.join(challenge_dir, "challenges.json")


@log_cache_status(logger)
@lru_cache()
def load_challenge_file() -> str:
    with open(challenge_file, "r") as challenge_fd:
        challenge_json = challenge_fd.read()

    return challenge_json


@cache_command()
def execute_command(command: str, challenge_identifier: str) -> dict:
    cmd_split = tuple(split_command(command))
    result: dict = c.run_command_parsed(cmd_split, challenge=challenge_identifier)
    return result
