import functools
import logging

logger = logging.getLogger(__name__)


def log_command(docker_fn):
    @functools.wraps(docker_fn)
    def wrap_docker_function_and_log_command(*args, **kwargs):
        logger.debug("Running docker command with the following arguments" + str(args))
        return docker_fn(*args, **kwargs)

    return wrap_docker_function_and_log_command
