from flask import Flask, jsonify

from server.config import config as app_settings
from server.extensions import init_extensions, db


def create_app(script_info=None):
    # instantiate the app
    app = Flask(
        __name__
    )

    # set config
    app.config.from_object(app_settings)

    # set up extensions
    init_extensions(app)

    # Views
    init_blueprints(app)

    # error handlers
    @app.errorhandler(401)
    def unauthorized_page(error):
        return jsonify(dict(status="unauthorized")), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return jsonify(dict(status="unauthorized")), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify(dict(status="not found")), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return jsonify(dict(status="not found", error=str(error))), 500

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app


def init_blueprints(app):
    """ Register all blueprints"""
    # register blueprints
    from server.routes import routes
    app.register_blueprint(routes)
