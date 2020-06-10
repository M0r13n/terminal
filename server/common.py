import logging
import typing

from werkzeug.datastructures import Headers

from server.models import User, Badge, GameModes

logger = logging.getLogger(__name__)


def get_user(headers: Headers):
    uuid = headers.get('X-UUID')
    return User.query.get(uuid)


def log_command(user: User, command: str, challenge: str, result: dict) -> None:
    user.add_command(
        command_string=command,
        challenge_id=challenge,
        solved=result.get('success', False)
    )
    if user.mode == GameModes.BADGE:
        applicable_badges: typing.Set[Badge] = Badge.earned_through_action(user, command)
        user.add_new_badges(applicable_badges)
    logger.debug(f"User {user.uuid} submitted a solution for {challenge}. His command was [{command}] and it was {'true' if result['success'] else 'false'}.")
