import typing

from server.models import Challenge


def get_command_from_json(body: dict) -> str:
    return body["command"]


def get_challenge_from_json(body: dict) -> str:
    return body["challenge"]


def split_command(command_string: str) -> typing.List[str]:
    return command_string.split()


def is_valid_request_body(body: dict) -> typing.Tuple[bool, str]:
    """
    Expected data looks like: {"command": "ls -a", "challenge":"challenge_id"}
    """
    if not body:
        return True, "No data. Provide \"Command\" and \"Challenge\"."
    error, error_msg = False, ""
    if "command" not in body.keys():
        error, error_msg = True, "Missing Key \"Command\""
    elif "challenge" not in body.keys():
        error, error_msg = True, "Missing Key \"challenge\""
    elif not is_valid_challenge_identifier(body["challenge"]):
        error, error_msg = True, f"{body['challenge']} is an invalid challenge identifier"

    return error, error_msg


def is_valid_challenge_identifier(challenge_id: str) -> bool:
    return challenge_id in map(lambda x: x.identifier, Challenge.query.all())


def parse_request(json_body: dict) -> [str, str]:
    command = get_command_from_json(json_body)
    challenge = get_challenge_from_json(json_body)
    return command, challenge
