"""Configures server."""

from pyramid.config import Configurator
from pyramid.response import Response
from wsgiref.simple_server import make_server


def hello_world(request):
    """Test handler."""
    print('Incoming request')
    return Response('<body><h1>Hello World!</h1></body>')


if __name__ == '__main__':
    """Main entry."""
    config = Configurator()
    config.add_route('hello', '/')
    config.add_view(hello_world, route_name='hello')
    app = config.make_wsgi_app()
    server = make_server('127.0.0.1', 1337, app)
    server.serve_forever()
