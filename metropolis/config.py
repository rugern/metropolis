"""Creates configuration for the server."""

from pyramid.config import Configurator


def getConfig(settings):
    """Returns the server configuration."""
    config = Configurator(settings=settings)

    config.add_route('test', '/test')
    config.add_route('main', '/')
    config.scan('metropolis')

    return config
