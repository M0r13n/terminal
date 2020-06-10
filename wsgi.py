import logging

from server.app import create_app
from server.logging import setup_logger

app = create_app()
# Logging
setup_logger(level=logging.DEBUG if app.config['DEBUG'] else logging.INFO)
