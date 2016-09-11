"""A collection of all the routes."""

import os
from pyramid.response import Response
from pyramid.view import view_config
from jinja2 import Environment
from jinja2 import FileSystemLoader
from metropolis.brain import createIndicators


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@view_config(route_name='test', renderer='json')
def test(request):
    """Test handler."""
    return {'a': '1'}


@view_config(route_name='main')
def main(request):
    """Handler for serving HTML doc."""
    environment = Environment(loader=FileSystemLoader(THIS_DIR))
    template = environment.get_template('client/index.html')
    return Response(template.render(name='Nils'))


def indicators(request):
    """Handler for serving indicators as CSV."""
    indicators = createIndicators()
    return Response(indicators, content_type='text/plain')
