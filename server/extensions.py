from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from executor.run_cmd import CommandExecutor

db = SQLAlchemy()
cors = CORS()
c = CommandExecutor()


def init_extensions(app):
    db.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
