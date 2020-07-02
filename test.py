"""
Loop over all challenges, run their example command and check for success.
"""

import os

import json
from server.challenges import challenge_dir
from executor.docker_config import volume_dir
from executor.run_cmd import CommandExecutor


basedir = os.path.abspath(os.path.dirname(__file__))
volume_dir = os.path.join(basedir, "executor/docker_image/ro_volume/")

def get_challenges():
    challenge_file = os.path.join(volume_dir, "challenges.json")
    with open(challenge_file, "rb") as challenge_file:
        challenge_json = json.loads(challenge_file.read()) 
    
    return challenge_json


def check_command(command, id):
    result = runner.run_command_parsed(tuple(command.split()), challenge_id)
    success = result['success']
    if not success:
        raise ValueError(f"{challenge_id} FAILED. Output was", result)
    else:
        print(f"{challenge_id} succeeded! :-)")

if __name__ == "__main__":
    runner = CommandExecutor()
    
    challenges = get_challenges()
    for challenge_id, challenge_definition in challenges.items():
        example_solution = challenge_definition['solution']
        check_command(example_solution, challenge_id)
    
    print("SUCCESS")