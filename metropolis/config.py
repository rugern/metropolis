"""Creates configuration for the server."""

from pyramid.config import Configurator

import metropolis.routes as routes

def getConfig(settings):
    """Returns the server configuration."""
    config = Configurator(settings=settings)
    config.add_route('hello', '/')
    config.add_view(routes.test, route_name='hello')
    return config
