import logging

from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import StatementError

from server.challenges import execute_command
from server.common import get_user, log_command
from server.extensions import db
from server.models import User, Badge, Challenge, FinalFeedback
from server.parse import is_valid_request_body, parse_request

routes = Blueprint("manage", __name__)
logger = logging.getLogger(__name__)


@routes.route('/command/run', methods=['GET', 'POST'])
def run_command():
    json_body = request.get_json(silent=True)
    error, error_msg = is_valid_request_body(json_body)
    if not error:
        command, challenge = parse_request(json_body)
        result: dict = execute_command(command, challenge)
        if not result:
            return jsonify(dict(success=False, error="Could not execute!")), 400
        user = get_user(request.headers)
        if user:
            log_command(user, command, challenge, result)
            result['badges'] = [badge.id for badge in user.badges]

        return jsonify(result), 200

    return jsonify(dict(success=False, error=error_msg)), 400


@routes.route('/session/new', methods=['GET'])
def get_settings():
    user = User.create_user()
    return jsonify(user.to_dict())


@routes.route('/challenge/list', methods=['GET'])
def list_challenges():
    challenges = Challenge.json_list()
    return jsonify(challenges), 200


@routes.route('/badges/list', methods=['GET'])
def list_badges():
    badges = Badge.json_list()
    return jsonify(badges), 200


@routes.route('/user/<string:uuid>/state', methods=['GET'])
def get_user_state(uuid: str):
    user: User = User.query.get(uuid)
    if not user:
        abort(404)
    state = dict(
        badges=[badge.id for badge in user.badges],
        mode=user.mode.value,
        solved_challenges=[challenge.solved_challenge.identifier for challenge in user.solved_challenges]
    )
    return jsonify(state), 200


@routes.route('/feedback', methods=['POST'])
def submit_feedback():
    user: User = get_user(request.headers)
    if not user:
        return jsonify(dict(error="Unknown User")), 404

    json_body = request.form

    if not json_body:
        return jsonify(dict(error="Missing JSON")), 400

    if 'feedback' not in json_body.keys():
        return jsonify(dict(error="Missing key \'feedback\'")), 400

    try:
        feedback = json_body['feedback']
        if not isinstance(feedback, int):
            feedback = int(feedback)
        user.feedback.append(FinalFeedback.create(motivation=feedback))
    except (KeyError, IndexError, ValueError):
        return jsonify(dict(error="Invalid Feedback")), 400
    except StatementError:
        db.session.rollback()
        return jsonify(dict(error="Invalid Feedback")), 400

    return jsonify(dict(success=True)), 201
