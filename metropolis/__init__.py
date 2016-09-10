"""Configures server."""

from metropolis.config import getConfig


def main(global_config, **settings):
    """Main entry."""
    config = getConfig(settings)
    return config.make_wsgi_app()
