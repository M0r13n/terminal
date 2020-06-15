# project/server/config.py

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME", "PricePicker-v2")
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    FLASK_DEBUG = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///../test.db")


class ProductionConfig(BaseConfig):
    """Production configuration."""
    FLASK_DEBUG = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///../test.db")


config = os.getenv(
    "APP_SETTINGS", "server.config.ProductionConfig"
)
