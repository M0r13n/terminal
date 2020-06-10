import functools
import hashlib
import typing

from server.models import CommandCache


def hash_cmd(command: str):
    command_encoded = command.encode('utf-8')
    digest = hashlib.sha224(command_encoded).hexdigest()
    return digest


def get_from_cache(command: str, challenge_identifier: str) -> typing.Optional[CommandCache]:
    c = CommandCache.get_by_pks(hash=hash_cmd(command), challenge_identifier=challenge_identifier)
    return c


def cache(command: str, challenge_identifier: str, result: dict) -> CommandCache:
    c = CommandCache.create(
        hash=hash_cmd(command),
        challenge_identifier=challenge_identifier,
        cmd_correct=result['success'],
        cmd_output=result['output']
    )
    return c


def cache_command():
    def wrapper(func):
        @functools.wraps(func)
        def wrap_func(command: str, challenge_identifier: str):
            cached_result = get_from_cache(command, challenge_identifier)
            if cached_result:
                result: dict = dict(success=cached_result.cmd_correct, output=cached_result.cmd_output, cached=True)
            else:
                result: dict = func(command, challenge_identifier)
                result['cached'] = False
                cache(command, challenge_identifier, result)
            return result

        return wrap_func

    return wrapper
