"""
Custom Context manager for limiting the total execution time of a docker container.
"""
import logging
import time

from docker.errors import ContainerError, NotFound, APIError
from requests import HTTPError
from requests.exceptions import SSLError

TIMEOUT_RESPONSE = b"""{"success":false, "output":"Command timed out"}"""
DEFAULT_FAIL_RESPONSE = b"""{"success":false, "output":"Docker execution failed."}"""

logger = logging.getLogger(__name__)


class ContainerTimeout(object):

    def __init__(self, timeout=5):
        self.container = None
        self.timeout = timeout
        self.container_output = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Wait for the container to return and pull output.
        Removes container afterwards.
        Also stops long running containers
        """
        try:
            self.wait_for_output()
        except ContainerError as error:
            logger.error(error)
            self.container_output = DEFAULT_FAIL_RESPONSE
        except (SSLError, NotFound, APIError, HTTPError) as error:
            logger.error(error)
            self.container_output = DEFAULT_FAIL_RESPONSE
        except TimeoutError:
            logger.warning("Container timed out!")
            self.container_output = TIMEOUT_RESPONSE
        finally:
            if self.container:
                # always clean up
                self.container.stop()
                self.container.remove()
            # always suppress exceptions
            return True

    def wait_for_output(self):
        """
        Wait timeout seconds for container to finish.
        Raises an TimeoutError if the containers runs longer than timeout.
        """
        i = 0
        while True:
            self.container_output = self.container.logs()
            if self.container_output:
                return True
            i += 1
            if i >= self.timeout:
                raise TimeoutError()
            time.sleep(1)
