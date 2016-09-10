"""Configures server."""

from wsgiref.simple_server import make_server
from metropolis.config import getConfig


def main(global_config, **settings):
    """Main entry."""
    config = getConfig(settings)
    return config.make_wsgi_app()
